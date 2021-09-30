from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.core.models import ProductenCatalogus
from sdg.producten.models import LocalizedProduct

User = get_user_model()


class GeneriekProduct(models.Model):
    """
    Generic product

    Container for localized generic products holding only the properties that
    are the same for every localized generic product.
    """

    upn = models.ForeignKey(
        "core.UniformeProductnaam",
        on_delete=models.PROTECT,
        related_name="generiek_product",
        help_text=_("De uniforme productnaam met betrekking tot dit product."),
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.PROTECT,
        related_name="generiek_informatie",
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de landelijke informatie"),
    )
    verplicht_product = models.BooleanField(
        _("verplicht product"),
        help_text=_(
            "Geeft aan of decentrale overheden verplicht zijn informatie over dit product te leveren."
        ),
    )

    @property
    def upn_uri(self):
        return self.upn.upn_uri

    @property
    def upn_label(self):
        return self.upn.upn_label

    def __str__(self):
        return f"{self.upn.upn_label}"

    class Meta:
        verbose_name = _("generiek product")
        verbose_name_plural = _("generieke producten")


class Product(models.Model):
    """
    Product

    Container for localized products holding only the properties that are the
    same for every localized product.
    """

    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct",
        related_name="producten",
        on_delete=models.PROTECT,
        verbose_name=_("generiek product"),
        help_text=_("Het generiek product voor het referentieproduct."),
        blank=True,
        null=True,
    )
    referentie_product = models.ForeignKey(
        "self",
        related_name="specifieke_producten",
        on_delete=models.SET_NULL,
        verbose_name=_("referentie product"),
        help_text=_(
            "Een referentie naar een product. "
            "Het toewijzen van een referentieproduct veronderstelt automatisch dat dit product specifiek is."
        ),
        blank=True,
        null=True,
    )
    catalogus = models.ForeignKey(
        "core.ProductenCatalogus",
        on_delete=models.CASCADE,
        related_name="producten",
        verbose_name=_("catalogus"),
        help_text=_("De catalogus waartoe dit product behoort."),
    )
    gerelateerde_producten = models.ManyToManyField(
        "self",
        related_name="gerelateerde_producten",
        blank=True,
        verbose_name=_("gerelateerd aan"),
        help_text=_("Een verwijzing naar een gerelateerd product."),
    )
    doelgroep = ChoiceArrayField(
        base_field=models.CharField(max_length=32, choices=DoelgroepChoices.choices),
        help_text=_(
            "Geeft aan voor welke doelgroep het product is bedoeld: burgers, bedrijven of burgers en bedrijven. Wordt "
            "gebruikt wanneer een portaal informatie over het product ophaalt uit de invoervoorziening. Zo krijgen de "
            "ondernemersportalen de ondernemersvariant en de burgerportalen de burgervariant. "
        ),
        default=list,
    )
    beschikbaar = models.BooleanField(
        _("beschikbaar"),
        help_text=_("Geeft aan of het product al dan niet beschikbaar is."),
        default=False,
    )
    lokaties = models.ManyToManyField(
        "organisaties.Lokatie",
        verbose_name=_("lokaties"),
        related_name="producten",
        help_text=_(
            "De locaties die zijn toegewezen aan de product.",
        ),
        blank=True,
    )

    @property
    def upn_uri(self):
        return self.generic_product.upn.upn_uri

    @property
    def upn_label(self):
        return self.generic_product.upn.upn_label

    @cached_property
    def beschikbare_talen(self):
        return {
            i.get_taal_display(): i.taal for i in self.laatste_versie.vertalingen.all()
        }

    @cached_property
    def is_referentie_product(self) -> bool:
        """:returns: Whether this is a reference product or not."""
        return bool(not self.referentie_product)

    @cached_property
    def laatste_versie(self):
        """:returns: Latest version for this product."""

        return (
            self.versies.filter(publicatie_datum__lte=now())
            .order_by("publicatie_datum")
            .first()
        )

    @cached_property
    def laatste_ongepubliceerde_versie(self):
        """:returns: Latest unpublished version for this product."""
        return self.versies.order_by("publicatie_datum").first()

    @cached_property
    def generic_product(self):
        """:returns: The generic product of this product."""

        return (
            self.generiek_product
            if self.is_referentie_product
            else self.referentie_product.generiek_product
        )

    def create_version_from_reference(self) -> ProductVersie:
        """Create fist version for this product based on latest reference version."""
        if self.is_referentie_product:
            raise ValueError(
                "create_version_from_reference must be called on a specific product"
            )
        return ProductVersie.objects.create(
            product=self,
            gemaakt_door=self.referentie_product.laatste_versie.gemaakt_door,
            publicatie_datum=now(),
        )

    def localize_version_from_reference(self, version: ProductVersie):
        """Create localized product information for this specific product based on available reference languages."""

        if self.is_referentie_product:
            raise ValueError(
                "localize_from_reference must be called on a specific product"
            )

        LocalizedProduct.objects.bulk_create(
            [
                version.generate_localized_information(taal=taal)
                for taal in self.referentie_product.beschikbare_talen.values()
            ],
            ignore_conflicts=True,
        )

    def get_or_create_specific_product(self, specific_catalog) -> Product:
        """Create a specific product for a reference product, including localized information."""

        if self.is_referentie_product:
            with transaction.atomic():
                if not isinstance(specific_catalog, Model):
                    specific_catalog = get_object_or_404(
                        ProductenCatalogus, pk=specific_catalog
                    )
                specific_product, created = Product.objects.get_or_create(
                    referentie_product=self,
                    catalogus=specific_catalog,
                    defaults={
                        "doelgroep": self.doelgroep,
                    },
                )
                version = specific_product.create_version_from_reference()
                specific_product.localize_version_from_reference(version)
                return specific_product
        else:
            return self

    def get_absolute_url(self):
        return reverse("producten:detail", kwargs={"pk": self.pk})

    def __str__(self):
        if self.is_referentie_product:
            return f"{self.generiek_product.upn_label} (referentie)"
        else:
            return f"{self.referentie_product.upn_label}"

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("producten")

    def clean(self):
        from sdg.producten.models.validators import (
            validate_reference_product,
            validate_specific_product,
        )

        super().clean()

        if self.is_referentie_product:
            validate_reference_product(self)
        else:
            validate_specific_product(self)


class ProductVersie(models.Model):
    """
    Product Version

    The version of a product.
    """

    product = models.ForeignKey(
        "producten.Product",
        related_name="versies",
        on_delete=models.PROTECT,
        verbose_name=_("product"),
        help_text=_("Het product voor het product versie."),
    )
    gemaakt_door = models.ForeignKey(
        User,
        related_name="productversies",
        on_delete=models.PROTECT,
        verbose_name=_("gemaakt_door"),
        help_text=_("De maker van deze productversie."),
    )
    versie = models.PositiveIntegerField(
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het product."),
        default=1,
    )

    publicatie_datum = models.DateTimeField(
        _("publicatie datum"),
        help_text=_("De datum van publicatie van de productversie."),
        blank=True,
        null=True,
    )
    gemaakt_op = models.DateTimeField(
        _("gemaakt op"),
        help_text=_("De oorspronkelijke aanmaakdatum voor deze productversie."),
        auto_now_add=True,
    )
    gewijzigd_op = models.DateTimeField(
        _("gewijzigd op"),
        help_text=_("De wijzigingsdatum voor deze productversie."),
        auto_now=True,
    )

    def generate_localized_information(self, taal, **kwargs) -> LocalizedProduct:
        """Generate localized information for this product."""
        return LocalizedProduct(
            product_versie=self,
            taal=taal,
            **kwargs,
        )

    def clean(self):
        super().clean()
        latest_unpublished_version = self.product.versies.order_by(
            "publicatie_datum"
        ).first()
        if self.publicatie_datum <= latest_unpublished_version.publicatie_datum:
            raise ValidationError(
                _(
                    "De publicatie datum kan niet vroeger zijn dan een toekomstige publicatiedatum."
                )
            )


class Productuitvoering(models.Model):
    """
    Product variant

    Container for localized product variants holding only the properties that
    are the same for every localized product variant.
    """

    product = models.ForeignKey(
        "producten.Product",
        related_name="uitvoeringen",
        on_delete=models.PROTECT,
        verbose_name=_("product"),
        help_text=_("Het product voor het productuitvoering."),
    )

    def __str__(self):
        return f"{self.product} (uitvoering)"

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

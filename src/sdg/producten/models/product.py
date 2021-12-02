from __future__ import annotations

import uuid
from datetime import date
from typing import Any, List

from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError, ValidationError
from django.db import models, transaction
from django.db.models import BooleanField, Case, Model, Q, Value, When
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.core.models import ProductenCatalogus
from sdg.producten.constants import PublishChoices
from sdg.producten.models import (
    LocalizedGeneriekProduct,
    LocalizedProduct,
    ProductFieldMixin,
)
from sdg.producten.models.managers import ProductQuerySet, ProductVersieQuerySet
from sdg.producten.utils import is_past_date

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
        related_name="generieke_producten",
        help_text=_("De uniforme productnaam met betrekking tot dit product."),
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.PROTECT,
        related_name="generiek_informatie",
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de landelijke informatie"),
        blank=True,
        null=True,
    )
    verplicht_product = models.BooleanField(
        _("verplicht product"),
        help_text=_(
            "Geeft aan of decentrale overheden verplicht zijn informatie over dit product te leveren."
        ),
        default=False,
    )

    @property
    def upn_uri(self):
        return self.upn.upn_uri

    @property
    def upn_label(self):
        return self.upn.upn_label

    def generate_localized_information(
        self, language, **kwargs
    ) -> LocalizedGeneriekProduct:
        """Generate localized information for this generic product."""
        return LocalizedGeneriekProduct(
            generiek_product=self,
            taal=language,
            **kwargs,
        )

    class Meta:
        verbose_name = _("generiek product")
        verbose_name_plural = _("generieke producten")

    def __str__(self):
        return f"{self.upn.upn_label}"


class Product(ProductFieldMixin, models.Model):
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
    product_aanwezig = models.BooleanField(
        _("product aanwezig"),
        help_text=_("Voert u dit product?"),
        blank=True,
        null=True,
    )
    product_aanwezig_toelichting = models.TextField(
        _("product aanwezig toelichting"),
        help_text=_("Toelichting"),
        blank=True,
        default="",
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
    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            "De identificatie die binnen deze API gebruikt wordt voor de resource."
        ),
    )

    objects = ProductQuerySet.as_manager()

    @property
    def upn_uri(self):
        return self.upn.upn_uri

    @property
    def upn_label(self):
        return self.upn.upn_label

    @cached_property
    def beschikbare_talen(self) -> dict:
        most_recent_version = self.get_most_recent_version
        if most_recent_version:
            return {
                i.get_taal_display(): i.taal for i in most_recent_version.vertalingen.all()
            }

        return {}

    @cached_property
    def is_referentie_product(self) -> bool:
        """:returns: Whether this is a reference product or not."""
        return bool(not self.referentie_product)

    @cached_property
    def has_expired(self) -> bool:
        """:returns: Whether this product has expired in relation to the reference product."""
        if self.is_referentie_product:
            return False
        if not self.laatste_versie:
            return False

        publication_date = self.laatste_versie.publicatie_datum
        reference_publication_date = self.laatste_versie.publicatie_datum

        return bool(
            (publication_date and reference_publication_date)
            and (publication_date < reference_publication_date)
        )

    @cached_property
    def get_most_recent_version(self):
        """
        Returns the most recent `ProductVersie`.
        """
        # Check if prefetch cache is available from the manager.
        result = getattr(self, "most_recent_version", None)

        # If not, retrieve it via the manager for consistancy.
        if result is None:
            p = self.__class__.objects.most_recent().filter(pk=self.pk).first()
            result = p.most_recent_version

        # If there's a version, return it.
        if result:
            return result[0]

        return None

    @cached_property
    def laatste_versie(self):  # TODO: optimize
        """:returns: Latest version (can be published, concept or scheduled) for this product."""
        latest_version = self.get_latest_versions(1)
        return latest_version[0] if latest_version else None

    @cached_property
    def laatste_actieve_versie(self):
        """:returns: Latest active version for this product."""
        latest_version = self.get_latest_versions(1, active=True)
        return latest_version[0] if latest_version else None

    @cached_property
    def generic_product(self):
        """:returns: The generic product of this product."""

        return (
            self.generiek_product
            if self.is_referentie_product
            else self.referentie_product.generiek_product
        )

    @cached_property
    def reference_product(self):
        """:returns: The reference product of this product."""
        return self if self.is_referentie_product else self.referentie_product

    @cached_property
    def upn(self):
        return self.generic_product.upn

    def get_active_field(self, field_name, default=None):
        """
        Get specific field value from `active_versions`.
        Validate that `active_versions` equals 1.
        """
        active_versions = getattr(self, "active_versions", None)

        if not active_versions:
            return default

        if len(active_versions) != 1:
            raise FieldError("Active version must be equal to 1")

        return getattr(active_versions[0], field_name)

    def get_municipality_locations(self):
        """:returns: All available locations for this product. Selected locations are labeled as a boolean."""
        return self.catalogus.lokale_overheid.lokaties.annotate(
            is_product_location=Case(
                When(
                    Q(pk__in=self.lokaties.all().values_list("pk")),
                    then=Value(True),
                ),
                output_field=BooleanField(default=False),
            ),
        )

    def get_latest_versions(self, quantity=5, active=False, exclude_concept=False):
        """:returns: The latest N versions for this product."""
        queryset = self.versies.all().order_by("-versie")

        if active:
            queryset = queryset.filter(publicatie_datum__lte=date.today())
        if exclude_concept:
            queryset = queryset.exclude(publicatie_datum=None)

        return queryset[:quantity:-1]

    def create_version_from_reference(self) -> ProductVersie:
        """Create fist version for this product based on latest reference version."""
        if self.is_referentie_product:
            raise ValueError(
                "create_version_from_reference must be called on a specific product"
            )
        return ProductVersie.objects.create(
            product=self,
            gemaakt_door=self.referentie_product.laatste_versie.gemaakt_door,
            publicatie_datum=None,
        )

    def localize_version_from_reference(
        self, version: ProductVersie, field_names: List[str]
    ):
        """Create localized product information for this specific product based on available reference languages."""
        if self.is_referentie_product:
            raise ValueError(
                "localize_from_reference must be called on a specific product"
            )

        localized_objects = [
            version.generate_localized_information(
                language=translation.taal,
                **{field: getattr(translation, field) for field in field_names},
            )
            for translation in self.referentie_product.laatste_versie.vertalingen.all()
        ]
        LocalizedProduct.objects.bulk_create(localized_objects, ignore_conflicts=True)

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

                lokaties = list(
                    specific_catalog.lokale_overheid.lokaties.all()
                )  # extra query, could be removed
                if len(lokaties) == 1:
                    specific_product.lokaties.add(lokaties[0])
                    specific_product.save()

                version = specific_product.create_version_from_reference()
                specific_product.localize_version_from_reference(
                    version,
                    field_names=[
                        "bezwaar_en_beroep",
                        "decentrale_link",
                        "decentrale_procedure_link",
                        "kosten_en_betaalmethoden",
                        "procedure_beschrijving",
                        "product_titel_decentraal",
                        "specifieke_tekst",
                        "uiterste_termijn",
                        "vereisten",
                        "verwijzing_links",
                        "wtd_bij_geen_reactie",
                    ],
                )
                return specific_product
        else:
            return self

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("producten")

    def __str__(self):
        if self.is_referentie_product:
            return f"{self.generiek_product.upn_label} (referentie)"
        else:
            return f"{self.referentie_product.upn_label}"

    def get_absolute_url(self):
        return reverse(
            "organisaties:catalogi:producten:detail",
            kwargs={
                "pk": self.catalogus.lokale_overheid.pk,
                "catalog_pk": self.catalogus.pk,
                "product_pk": self.pk,
            },
        )

    def clean(self):
        from sdg.producten.models.validators import (
            validate_product,
            validate_reference_product,
            validate_specific_product,
        )

        super().clean()

        validate_product(self)

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
        on_delete=models.CASCADE,
        verbose_name=_("product"),
        help_text=_("Het product voor het product versie."),
        blank=True,
    )
    gemaakt_door = models.ForeignKey(
        User,
        related_name="productversies",
        on_delete=models.PROTECT,
        verbose_name=_("gemaakt door"),
        help_text=_("De maker van deze productversie."),
        blank=True,
        null=True,
    )
    versie = models.PositiveIntegerField(
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het product."),
        default=1,
        blank=True,
    )

    publicatie_datum = models.DateField(
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

    objects = ProductVersieQuerySet.as_manager()

    def get_published_status(self) -> Any[PublishChoices.choices]:
        """:returns: The current published status for this product version."""
        if not self.publicatie_datum:
            return PublishChoices.concept
        elif self.publicatie_datum <= date.today():
            return PublishChoices.now
        else:
            return PublishChoices.later

    def generate_localized_information(self, language, **kwargs) -> LocalizedProduct:
        """Generate localized information for this product."""
        return LocalizedProduct(
            product_versie=self,
            taal=language,
            **kwargs,
        )

    class Meta:
        verbose_name = _("product versie")
        verbose_name_plural = _("product versies")
        ordering = ("-versie",)

    def __str__(self):
        return f"{self.product} - {self.versie}"

    def clean(self):
        super().clean()

        if not self.pk:
            # Validators for new instances
            if self.publicatie_datum and is_past_date(self.publicatie_datum):
                raise ValidationError(
                    _("De publicatiedatum kan niet in het verleden liggen.")
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

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

    def __str__(self):
        return f"{self.product} (uitvoering)"

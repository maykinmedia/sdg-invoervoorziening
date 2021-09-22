from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.producten.models import LocalizedProduct


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
    versie = models.PositiveIntegerField(
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het item."),
        default=1,
    )
    publicatie_datum = models.DateTimeField(
        _("publicatie datum"), help_text=_("De datum van publicatie van de product.")
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
        return self.get_generic_product().upn.upn_uri

    @property
    def upn_label(self):
        return self.get_generic_product().upn.upn_label

    @cached_property
    def beschikbare_talen(self):
        return [i.taal for i in self.vertalingen.all()]

    def is_reference_product(self) -> bool:
        return bool(not self.referentie_product)

    def get_generic_product(self):
        """
        :returns: Generiek product voor het product.
        """
        return (
            self.generiek_product
            if self.is_reference_product()
            else self.referentie_product.generiek_product
        )

    def generate_informatie(self, taal, **kwargs) -> LocalizedProduct:
        """Generate localized information for this product."""
        return LocalizedProduct(
            product=self,
            taal=taal,
            **kwargs,
        )

    def get_or_create_specific_product(self) -> Product:
        """Maak een specifiek product voor een referentieproduct, inclusief gelokaliseerde informatie."""

        if self.is_reference_product():
            specific_product, created = Product.objects.get_or_create(
                referentie_product=self,
                defaults={
                    "catalogus": self.catalogus.specifiek_catalog.get(),
                    "doelgroep": self.doelgroep,
                    "publicatie_datum": self.publicatie_datum,
                },
            )
            if created:
                LocalizedProduct.objects.bulk_create(
                    [
                        specific_product.generate_informatie(taal=taal)
                        for taal in self.beschikbare_talen
                    ]
                )
            return specific_product
        else:
            return self

    def get_absolute_url(self):
        return reverse("producten:detail", kwargs={"pk": self.pk})

    def __str__(self):
        if self.is_reference_product():
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

        if self.is_reference_product():
            validate_reference_product(self)
        else:
            validate_specific_product(self)


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
        verbose_name=_("referentie"),
        help_text=_("Het referentieproduct voor het product."),
    )

    def __str__(self):
        return f"{self.product} (uitvoering)"

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

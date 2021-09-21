from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.core.models import ProductenCatalogus
from sdg.producten.models import ProductInformatie


class GeneriekProduct(models.Model):
    """Een generiek product.
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

    upn = models.ForeignKey(
        "core.UniformeProductnaam",
        on_delete=models.PROTECT,
        related_name="generiek_product",
        verbose_name=_("uniforme productnaam"),
        help_text=_("De uniforme productnaam met betrekking tot dit product."),
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
        verbose_name_plural = _("generiek product")


class Product(models.Model):
    """Een product.
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

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
        help_text=_("Referentie naar de catalogus waartoe dit product behoort."),
    )

    product = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        related_name="gerefereerd",
        null=True,
        blank=True,
        verbose_name=_("refereert aan"),
        help_text=_("Een verwijzing naar een ander product."),
    )
    gerelateerd_product = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="gerelateerd",
        null=True,
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
        _("publicatie datum"),
        help_text=_("De datum van publicatie van de product."),
        auto_now_add=True,
    )
    lokaties = models.ManyToManyField(
        "organisaties.Lokatie",
        verbose_name=_("lokaties"),
        related_name="producten",
        help_text=_(
            "De locaties die zijn toegewezen aan de product.",
        ),
    )

    @property
    def upn_uri(self):
        return self.get_generic_product().upn.upn_uri

    @property
    def upn_label(self):
        return self.get_generic_product().upn.upn_label

    @cached_property
    def beschikbare_talen(self):
        """Naast de taal van de informatie, dient ook aangegeven te worden in welke aanvullende taal/talen de
        procedure kan worden uitgevoerd. elke productbeschrijving is in één taal (nl of en). De 'additional
        languages' betreft dus altijd de andere taal (en of nl). Aanname: de portalen richten zich uitsluitend op
        Nederlands en Engels, geen andere talen"""
        return [i.taal for i in self.informatie.all()]

    def is_reference_product(self) -> bool:
        """Dit product is een referentieproduct, omdat het geen referentieproduct heeft."""
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

    def generate_informatie(self, taal, **kwargs) -> ProductInformatie:
        """Generate localized information for this product."""
        return ProductInformatie(
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
                },
            )
            if created:
                ProductInformatie.objects.bulk_create(
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
            return f"{self.generiek_product.upn_label} [referentie]"
        else:
            return f"{self.referentie_product.upn_label}"

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("product")

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
    """Een productuitvoering (variantvorm van een specifiek product).
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

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
        verbose_name_plural = _("productuitvoering")

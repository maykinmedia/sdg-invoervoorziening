from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField


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

    def __str__(self):
        return f"{self.upn.upn_label}"

    class Meta:
        verbose_name = _("generiek product")
        verbose_name_plural = _("generiek product")


class SpecifiekProduct(models.Model):
    """Een specifiek product.
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct",
        related_name="specifiek",
        on_delete=models.PROTECT,
        verbose_name=_("generiek product"),
        help_text=_("Het generiek product voor het specifieke product."),
        blank=True,
        null=True,
    )
    referentie_product = models.ForeignKey(
        "self",
        related_name="original",
        on_delete=models.PROTECT,
        verbose_name=_("referentie product"),
        help_text=_("Het referentie product voor het specifieke product."),
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
        blank=True,
    )
    beschikbaar = models.BooleanField(
        _("beschikbaar"),
        help_text=_("Geeft aan of het product al dan niet beschikbaar is."),
    )
    versie = models.PositiveIntegerField(
        default=1,
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het item."),
    )
    publicatie_datum = models.DateTimeField(
        _("publicatie datum"),
        help_text=_("De datum van publicatie van de productspecifieke informatie."),
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
        return self.generiek_product.upn_uri

    @cached_property
    def beschikbare_talen(self):
        """Naast de taal van de informatie, dient ook aangegeven te worden in welke aanvullende taal/talen de
        procedure kan worden uitgevoerd. elke productbeschrijving is in één taal (nl of en). De 'additional
        languages' betreft dus altijd de andere taal (en of nl). Aanname: de portalen richten zich uitsluitend op
        Nederlands en Engels, geen andere talen"""

        return [i.taal for i in self.informatie.all()]

    def get_absolute_url(self):
        return reverse("producten:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.generiek_product} (specifiek)"

    class Meta:
        verbose_name = _("specifiek product")
        verbose_name_plural = _("specifiek product")

    def clean(self):
        super().clean()

        if not self.referentie_product.catalogus.is_referentie_catalogus:
            raise ValidationError(
                _(
                    """"Het referentieproduct van dit product moet in een referentiecatalogus staan."""
                )
            )

        if self.generiek_product and not self.catalogus.is_referentie_catalogus:
            raise ValidationError(
                _(
                    """Het veld "generiek_product" kan alleen worden toegevoegd als dit product een referentieproduct
                    is. """
                )
            )


class Productuitvoering(models.Model):
    """Een productuitvoering (variantvorm van een specifiek product).
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

    specifiek_product = models.ForeignKey(
        "producten.SpecifiekProduct",
        related_name="uitvoeringen",
        on_delete=models.PROTECT,
        verbose_name=_("referentie"),
        help_text=_("Het referentieproduct voor het specifieke product."),
    )

    def __str__(self):
        return f"{self.specifiek_product} (uitvoering)"

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoering")

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import DoelgroepChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.producten.models import ProductGegevensMixin


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


class ReferentieProduct(models.Model):
    """Een referentie product.
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

    generiek = models.OneToOneField(
        "producten.GeneriekProduct",
        related_name="referentie",
        on_delete=models.PROTECT,
        verbose_name=_("generiek"),
        help_text=_("Het generieke moederproduct voor deze referentie."),
    )

    @property
    def upn_uri(self):
        return self.generiek.upn.upn_uri

    @property
    def upn_label(self):
        return self.generiek.upn.upn_label

    @cached_property
    def beschikbare_talen(self):
        """Naast de taal van de informatie, dient ook aangegeven te worden in welke aanvullende taal/talen de
        procedure kan worden uitgevoerd. elke productbeschrijving is in één taal (nl of en). De 'additional
        languages' betreft dus altijd de andere taal (en of nl). Aanname: de portalen richten zich uitsluitend op
        Nederlands en Engels, geen andere talen"""

        return [i.taal for i in self.informatie.all()]

    def get_absolute_url(self):
        return reverse("producten:ref_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.upn_label} (referentie)"

    class Meta:
        verbose_name = _("referentie product")
        verbose_name_plural = _("referentie product")


class SpecifiekProduct(models.Model):
    """Een specifiek product.
    Kan meerdere lokaal-specifieke varianten van productinformatie bevatten."""

    referentie = models.ForeignKey(
        "producten.ReferentieProduct",
        related_name="specifiek",
        on_delete=models.PROTECT,
        verbose_name=_("referentie"),
        help_text=_("Het referentieproduct voor het specifieke product."),
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
        return self.referentie.upn_uri

    @property
    def upn_label(self):
        return self.referentie.upn_label

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
        return f"{self.referentie.upn_label} (specifiek)"

    class Meta:
        verbose_name = _("specifiek product")
        verbose_name_plural = _("specifiek product")


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
        return f"{self.specifiek_product.upn_label} (uitvoering)"

    class Meta:
        verbose_name = _("specifiek product")
        verbose_name_plural = _("specifiek product")

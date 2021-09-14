from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.core.constants import DoelgroepChoices, TaalChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.producten.models.mixins import ProductGegevensMixin


class ProductGeneriekInformatie(models.Model):
    """De generiek informatie over een product."""

    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct",
        on_delete=models.PROTECT,
        related_name="informatie",
        verbose_name=_("generiek product"),
        help_text=_("Het generieke moederproduct van deze informatie."),
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.PROTECT,
        related_name="generiek_informatie",
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de landelijke informatie"),
    )
    taal = models.CharField(
        _("taal"),
        choices=TaalChoices.choices,
        max_length=3,
        help_text=_(
            "De taal waarin de betreffende tekst is geschreven."
            "ISO 639 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)"
        ),
    )
    product_titel = models.CharField(
        _("product titel"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
    )
    generieke_tekst = MarkdownxField(
        _("generieke tekst"),
        help_text=_(
            "De Nationale Portalen schrijven een inleidende, algemene tekst over het product. Het idee is dat deze "
        ),
    )
    korte_omschrijving = models.CharField(
        _("korte omschrijving"),
        max_length=80,
        help_text=_(
            "Korte omschrijving van wat er op de pagina staat, gebruikt in de meta tags van de productpagina (meta "
            'name="description"). Deze tekst wordt gebruikt om te tonen wanneer de pagina wordt gevonden in een '
            "zoekmachine. "
        ),
    )
    datum_check = models.DateTimeField(
        _("datum check"),
        help_text=_(
            "De informatie over het product kan worden gewijzigd en gecontroleerd op actualiteit (gecheckt). De "
            "Nationale portalen houden bij wanneer de informatie voor het laasts is 'gecheckt'.  Deze datum wordt op "
            "het portaal getoond."
        ),
    )
    verwijzing_links = ArrayField(
        models.URLField(_("url van verwijzing"), max_length=1000),
        help_text=_(
            "Zowel de Nationale Portalen als de decentrale overheden kunnen een x-tal 'verwijzingen' opnemen bij een "
            "product. Voorstel hierbij om zo'n 'verwijzing' te laten bestaan uit een -bij elkaar horende-  "
            "beschrijving en hyperlink. De tekst van artikel 9 geeft enkele voorbeelden hiervan: 'richtsnoeren/ "
            "NEN-specs bijv en ook links naar de wetgeving (dit laatste is inderdaad te verstaan als vertaling van "
            "'Legal Acts'. Bart heeft dit bij Jurist van bNC (Vanessa) gecheckt. "
        ),
        blank=True,
        default=list,
    )
    landelijke_link = models.URLField(
        _("landelijke link"),
        help_text=_(
            "URL van de productpagina wanneer het een landelijk product betreft of de pagina met enkel generieke "
            "beschrijving van een decentraal product, bijvoorbeeld : "
            "https://ondernemersplein.kvk.nl/terrasvergunning. gebruikt voor o.a. notificeren, feedback & statistics "
            "en het kunnen bekijken van de generieke productinformatie (bv door gebruikers van de gemeentelijke "
            "invoervoorziening) "
        ),
    )
    verplicht_product = models.BooleanField(
        _("verplicht product"),
        help_text=_(
            "Geeft aan of decentrale overheden verplicht zijn informatie over dit product te leveren."
        ),
    )
    generieke_link = models.URLField(
        _("generieke link"),
        help_text=_(
            "URL van de productpagina wanneer het een landelijk product betreft of de pagina met enkel generieke "
            "beschrijving van een decentraal product, bijvoorbeeld : "
            "https://ondernemersplein.kvk.nl/terrasvergunning. gebruikt voor o.a. notificeren, feedback & statistics "
            "en het kunnen bekijken van de generieke productinformatie (bv door gebruikers van de gemeentelijke "
            "invoervoorziening) "
        ),
    )

    def __str__(self):
        return f"{self.generiek_product} [informatie]"

    class Meta:
        verbose_name = _("product generiek informatie")
        verbose_name_plural = _("product generiek informatie")


class ProductReferentieInformatie(ProductGegevensMixin, models.Model):
    """De specifieke informatie over een product."""

    referentie_product = models.ForeignKey(
        "producten.ReferentieProduct",
        on_delete=models.PROTECT,
        related_name="informatie",
        verbose_name=_("referentie product"),
        help_text=_("Het referentie moederproduct van deze informatie."),
    )

    def __str__(self):
        return f"{self.referentie_product} [informatie]"

    class Meta:
        verbose_name = _("product referentie informatie")
        verbose_name_plural = _("product referentie informatie")


class ProductSpecifiekInformatie(ProductGegevensMixin, models.Model):
    """De specifieke informatie over een product."""

    specifiek_product = models.ForeignKey(
        "producten.SpecifiekProduct",
        on_delete=models.PROTECT,
        related_name="informatie",
        verbose_name=_("specifiek product"),
        help_text=_("Het specifiek moederproduct van deze informatie."),
    )

    def __str__(self):
        return f"{self.specifiek_product} [informatie]"

    class Meta:
        verbose_name = _("product specifiek informatie")
        verbose_name_plural = _("product specifiek informatie")

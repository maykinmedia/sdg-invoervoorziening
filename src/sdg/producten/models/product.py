from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.core.constants import DoelgroepChoices, TaalChoices
from sdg.core.db.fields import ChoiceArrayField
from sdg.producten.models.mixins import (
    ProductAanvraagGegevensMixin,
    ProductGegevensMixin,
)


class ProductGeneriekInformatie(models.Model):
    """De generiek informatie over een product."""

    upn = models.ForeignKey(
        "core.UniformeProductnaam",
        on_delete=models.PROTECT,
        related_name="generiek_product",
        verbose_name=_("uniforme productnaam"),
        help_text=_("De uniforme productnaam met betrekking tot dit product."),
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

    @property
    def upn_uri(self):
        return self.upn.upn_uri

    def __str__(self):
        return f"{self.product_titel}"

    class Meta:
        verbose_name = _("product generiek informatie")
        verbose_name_plural = _("product generiek informatie")


class ProductSpecifiekInformatie(ProductGegevensMixin, models.Model):
    """De specifieke informatie over een product."""

    standaard = models.ForeignKey(
        "producten.StandaardProductSpecifiekInformatie",
        related_name="aanpassingen",
        on_delete=models.PROTECT,
        verbose_name=_("standaard"),
        help_text=_("De standaardinformatie voor de product specifiek informatie."),
    )
    generiek_product = models.OneToOneField(
        "ProductGeneriekInformatie",
        on_delete=models.PROTECT,
        related_name="specifiek_product",
        verbose_name=_("generiek product"),
        help_text=_("Een verwijzing naar de generieke versie van dit product"),
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
    catalogus = models.ForeignKey(
        "core.ProductenCatalogus",
        on_delete=models.CASCADE,
        related_name="producten",
        verbose_name=_("catalogus"),
        help_text=_("Referentie naar de catalogus waartoe dit product behoort."),
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

    @property
    def upn_uri(self):
        return self.generiek_product.upn_uri

    @property
    def taal(self):
        return self.generiek_product.taal

    def __str__(self):
        return f"{self.product_titel_decentraal} - {self.versie}"

    class Meta:
        verbose_name = _("product specifiek informatie")
        verbose_name_plural = _("product specifiek informatie")


class ProductSpecifiekAanvraag(ProductAanvraagGegevensMixin, models.Model):
    """De specifieke aanvraag van een product."""

    standaard = models.ForeignKey(
        "producten.StandaardProductSpecifiekAanvraag",
        related_name="aanpassingen",
        on_delete=models.PROTECT,
        verbose_name=_("standaard"),
        help_text=_("De standaardinformatie voor de product specifiek aanvraag."),
    )
    specifiek_product = models.ForeignKey(
        "ProductSpecifiekInformatie",
        on_delete=models.CASCADE,
        verbose_name=_("specifiek product"),
        related_name="specifiek_aanvraag",
    )
    lokaties = models.ManyToManyField(
        "organisaties.Lokatie",
        verbose_name=_("lokaties"),
        related_name="productaanvragen",
        help_text=_(
            "De locaties die zijn toegewezen aan de productaanvraag.",
        ),
    )

    @property
    def beschikbare_talen(self):
        """Naast de taal van de informatie, dient ook aangegeven te worden in welke aanvullende taal/talen de
        procedure kan worden uitgevoerd. elke productbeschrijving is in één taal (nl of en). De 'additional
        languages' betreft dus altijd de andere taal (en of nl). Aanname: de portalen richten zich uitsluitend op
        Nederlands en Engels, geen andere talen"""

        return [
            i
            for i in TaalChoices.get_available_languages()
            if i != self.specifiek_product.taal
        ]

    class Meta:
        verbose_name = _("product specifiek aanvraag")
        verbose_name_plural = _("product specifiek aanvragen")


class Productuitvoering(ProductGegevensMixin, models.Model):
    """De specifieke uitvoering van een product.
    Gemeente kan van een product meerdere varianten beschrijven."""

    standaard = models.ForeignKey(
        "producten.StandaardProductuitvoering",
        related_name="aanpassingen",
        on_delete=models.PROTECT,
        verbose_name=_("standaard"),
        help_text=_("De standaardinformatie voor de productuitvoering."),
    )
    product_specifiek_informatie = models.ForeignKey(
        "ProductSpecifiekInformatie",
        on_delete=models.CASCADE,
        verbose_name=_("product specifiek informatie"),
        help_text=_("Referentie naar het product specifiek informatie."),
    )
    product_specifiek_aanvraag = models.ForeignKey(
        "ProductSpecifiekAanvraag",
        on_delete=models.CASCADE,
        verbose_name=_("product specifiek aanvraag"),
        help_text=_("Referentie naar het product specifiek aanvraag."),
    )
    product_titel_uitvoering = models.CharField(
        _("product titel_uitovering"),
        max_length=50,
        help_text=_(
            "De titel van het  product, die immers kan afwijken van de landelijke titel."
        ),
    )

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

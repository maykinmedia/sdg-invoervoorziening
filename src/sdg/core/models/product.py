from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField

from sdg.core.constants import DoelgroepChoices, TaalChoices


class ProductGeneriekInformatie(models.Model):
    """De generiek informatie over een product."""

    verantwoordelijke_organisatie = models.ForeignKey(
        "Organisatie",
        on_delete=models.PROTECT,
        related_name="generiek_informatie",
        verbose_name=_("product generiek informatie"),
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
    upn_uri = models.URLField(
        _("UPN URI"),
        help_text=_(
            "Uniforme Productnaam URI van landelijk product",
        ),
    )
    upn_label = models.CharField(
        _("UPN label"),
        max_length=255,
        help_text=_(
            "Het bijbehorende label. Zie https://standaarden.overheid.nl/owms/oquery/UPL-actueel.plain voor de "
            "volledige UPL. "
        ),
    )
    product_titel = models.CharField(
        _("product titel"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
    )
    generieke_tekst = RichTextField(
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

    class Meta:
        abstract = True
        verbose_name = _("product generiek informatie")
        verbose_name_plural = _("product generiek informatie")


class ProductSpecifiekInformatie(ProductGeneriekInformatie, models.Model):
    """De specifieke informatie over een product."""

    catalogus = models.ForeignKey(
        "ProductenCatalogus",
        on_delete=models.CASCADE,
        related_name="producten",
        verbose_name=_("product specifiek informatie"),
        help_text=_("Referentie naar de catalogus waartoe dit product behoort."),
    )
    product = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        related_name="gerefereerd",
        null=True,
        blank=True,
        verbose_name="refereert aan",
        help_text=_("Object record which corrects the current record"),
    )
    doelgroep = ArrayField(
        models.CharField(max_length=32, choices=DoelgroepChoices.choices),
        help_text=_(
            "Geeft aan voor welke doelgroep het product is bedoeld: burgers, bedrijven of burgers en bedrijven. Wordt "
            "gebruikt wanneer een portaal informatie over het product ophaalt uit de invoervoorziening. Zo krijgen de "
            "ondernemersportalen de ondernemersvariant en de burgerportalen de burgervariant. "
        ),
        default=list,
        blank=True,
    )
    product_titel_decentraal = models.CharField(
        _("product titel decentraal"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
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

    class Meta:
        verbose_name = _("product specifiek informatie")
        verbose_name_plural = _("product specifiek informatie")


class ProductSpecifiekAanvraag(models.Model):
    """De specifieke aanvraag van een product."""

    product = models.ForeignKey(
        "ProductSpecifiekInformatie",
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
        related_name="specifiek_aanvraag",
    )
    beschikbare_talen = models.CharField(
        _("beschikbare talen"),
        max_length=255,
        help_text=_(
            "Naast de taal van de informatie, dient ook aangegeven te worden in welke aanvullende taal/talen de "
            "procedure kan worden uitgevoerd. elke productbeschrijving is in één taal (nl of en). De 'additional "
            "languages' betreft dus altijd de andere taal (en of nl). Aanname: de portalen richten zich uitsluitend "
            "op Nederlands en Engels, geen andere talen."
        ),
    )
    procedure_beschrijving = RichTextField(
        _("procedure beschrijving"),
        help_text=_(
            "Procedurebeschrijving.",
        ),
    )
    vereisten = RichTextField(
        _("vereisten"),
        help_text=_(
            "Vereisten auth/id/sign.",
        ),
    )
    bewijs = RichTextField(
        _("bewijs"),
        help_text=_(
            "Bewijs (type/format).",
        ),
    )
    bezwaar_en_beroep = RichTextField(
        _("bezwaar en beroep"),
        help_text=_(
            "Bezwaar en beroep.",
        ),
    )
    kosten_en_betaalmethoden = RichTextField(
        _("kosten en betaalmethoden"),
        help_text=_(
            "Kosten en betaalmethoden.",
        ),
    )
    uiterste_termijn = RichTextField(
        _("uiterste termijn"),
        help_text=_(
            "Deadlines.",
        ),
    )
    wtd_bij_geen_reactie = RichTextField(
        _("wtd bij geen reactie"),
        help_text=_(
            "Wat te doen bij geen reactie.",
        ),
    )
    decentrale_procedure_link = models.URLField(
        _("decentrale procedure link"),
        help_text=_("Link naar de procedure voor burgers en / of bedrijven."),
    )

    class Meta:
        verbose_name = _("product specifiek aanvraag")
        verbose_name_plural = _("product specifiek aanvragen")


class Productuitvoering(models.Model):
    """De specifieke uitvoering van een product.
    Gemeente kan van een product meerdere varianten beschrijven."""

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

    product_titel_decentraal = models.CharField(
        _("product titel decentraal"),
        max_length=50,
        help_text=_("Decentrale producttitel."),
    )
    specifieke_tekst = RichTextField(
        _("specifieke tekst"),
        help_text=_("Decentrale omschrijving."),
    )
    verwijzing_links = ArrayField(
        models.URLField(_("url van verwijzing"), max_length=1000),
        help_text=_("Decentrale verwijzingen."),
        blank=True,
        default=list,
    )

    specifieke_link = models.URLField(
        _("specifieke link"),
        help_text=_("URL decentrale productpagina."),
    )

    decentrale_link = models.URLField(
        _("decentrale link"),
        help_text=_(
            "Link naar decentrale productpagina voor burgers en / of bedrijven."
        ),
    )
    datum_wijziging = models.DateTimeField(
        _("datum wijziging"),
        help_text=_(
            "Decentrale overheden geven een wijzigingsdatum mee voor hun informatie. Deze datum wordt op het portaal getoond."
        ),
    )

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.producten.models.mixins import ProductFieldMixin, TaalMixin


class LocalizedGeneriekProduct(ProductFieldMixin, TaalMixin, models.Model):

    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct",
        on_delete=models.CASCADE,
        related_name="vertalingen",
        verbose_name=_("generiek product"),
        help_text=_("Het generieke product van deze vertaling."),
    )

    # See: UML Product (generiek)

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

    def __str__(self):
        return self.product_titel

    class Meta:
        verbose_name = _("Vertaald generiek product")
        verbose_name_plural = _("Vertaalde generieke producten")
        constraints = [
            models.UniqueConstraint(
                fields=["generiek_product", "taal"],
                name="unique_language_per_generiekproduct",
            )
        ]


class LocalizedProduct(ProductFieldMixin, TaalMixin, models.Model):

    product = models.ForeignKey(
        "producten.Product",
        on_delete=models.CASCADE,
        related_name="vertalingen",
        verbose_name=_("specifieke product"),
        help_text=_("Het specifieke product van deze vertaling."),
    )

    # See: UML Product (specifiek informatie)

    product_titel_decentraal = models.CharField(
        _("product titel decentraal"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
        blank=True,
    )
    specifieke_tekst = MarkdownxField(
        _("specifieke tekst"),
        help_text=_("Decentrale omschrijving."),
        blank=True,
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
        blank=True,
    )
    decentrale_link = models.URLField(
        _("decentrale link"),
        help_text=_(
            "Link naar decentrale productpagina voor burgers en / of bedrijven."
        ),
        blank=True,
    )
    datum_wijziging = models.DateTimeField(
        _("datum wijziging"),
        help_text=_(
            "Decentrale overheden geven een wijzigingsdatum mee voor hun informatie. Deze datum wordt op het portaal "
            "getoond. "
        ),
        auto_now=True,
    )

    # See: UML: Product (specifiek aanvraag)

    procedure_beschrijving = MarkdownxField(
        _("procedure beschrijving"),
        help_text=_(
            "Procedurebeschrijving.",
        ),
        blank=True,
    )
    vereisten = MarkdownxField(
        _("vereisten"),
        help_text=_(
            "Vereisten auth/id/sign.",
        ),
        blank=True,
    )
    bewijs = MarkdownxField(
        _("bewijs"),
        help_text=_(
            "Bewijs (type/format).",
        ),
        blank=True,
    )
    bezwaar_en_beroep = MarkdownxField(
        _("bezwaar en beroep"),
        help_text=_(
            "Bezwaar en beroep.",
        ),
        blank=True,
    )
    kosten_en_betaalmethoden = MarkdownxField(
        _("kosten en betaalmethoden"),
        help_text=_(
            "Kosten en betaalmethoden.",
        ),
        blank=True,
    )
    uiterste_termijn = MarkdownxField(
        _("uiterste termijn"),
        help_text=_(
            "Deadlines.",
        ),
        blank=True,
    )
    wtd_bij_geen_reactie = MarkdownxField(
        _("wtd bij geen reactie"),
        help_text=_(
            "Wat te doen bij geen reactie.",
        ),
        blank=True,
    )
    decentrale_procedure_link = models.URLField(
        _("decentrale procedure link"),
        help_text=_("Link naar de procedure voor burgers en / of bedrijven."),
        blank=True,
    )

    @cached_property
    def referentie_informatie(self):
        if self.product.referentie_product:
            return self.product.referentie_product.vertalingen.get(taal=self.taal)
        else:
            return None

    @cached_property
    def generiek_informatie(self):
        return self.product.get_generic_product().vertalingen.get(taal=self.taal)

    def __str__(self):
        return self.product_titel_decentraal

    class Meta:
        verbose_name = _("vertaald product")
        verbose_name_plural = _("vertaalde producten")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "taal"],
                name="unique_language_per_product",
            )
        ]


class LocalizedProductuitvoering(TaalMixin, models.Model):

    productuitvoering = models.ForeignKey(
        "producten.Productuitvoering",
        on_delete=models.CASCADE,
        related_name="vertalingen",
        verbose_name=_("productuitvoering"),
        help_text=_("De productuitvoering van deze vertaling."),
    )

    # See: UML Productuitvoering
    # Other fields are under discussion.

    product_titel_uitvoering = models.CharField(
        _("product titel uitvoering"),
        max_length=50,
        help_text=_("De titel van de uitvoering van het product."),
    )

    def __str__(self):
        return self.product_titel_uitvoering

    class Meta:
        verbose_name = _("vertaalde productuitvoering")
        verbose_name_plural = _("vertaalde productuitvoeringen")
        constraints = [
            models.UniqueConstraint(
                fields=["productuitvoering", "taal"],
                name="unique_language_per_productuitvoering",
            )
        ]

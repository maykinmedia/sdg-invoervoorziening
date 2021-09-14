from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.core.constants import TaalChoices


class ProductGegevensMixin(models.Model):
    taal = models.CharField(
        _("taal"),
        choices=TaalChoices.choices,
        max_length=3,
        help_text=_(
            "De taal waarin de betreffende tekst is geschreven."
            "ISO 639 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)"
        ),
    )
    product_titel_decentraal = models.CharField(
        _("product titel decentraal"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
    )
    specifieke_tekst = MarkdownxField(
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
            "Decentrale overheden geven een wijzigingsdatum mee voor hun informatie. Deze datum wordt op het portaal "
            "getoond. "
        ),
    )
    procedure_beschrijving = MarkdownxField(
        _("procedure beschrijving"),
        help_text=_(
            "Procedurebeschrijving.",
        ),
        blank=True,
        null=True,
    )
    vereisten = MarkdownxField(
        _("vereisten"),
        help_text=_(
            "Vereisten auth/id/sign.",
        ),
        blank=True,
        null=True,
    )
    bewijs = MarkdownxField(
        _("bewijs"),
        help_text=_(
            "Bewijs (type/format).",
        ),
        blank=True,
        null=True,
    )
    bezwaar_en_beroep = MarkdownxField(
        _("bezwaar en beroep"),
        help_text=_(
            "Bezwaar en beroep.",
        ),
        blank=True,
        null=True,
    )
    kosten_en_betaalmethoden = MarkdownxField(
        _("kosten en betaalmethoden"),
        help_text=_(
            "Kosten en betaalmethoden.",
        ),
        blank=True,
        null=True,
    )
    uiterste_termijn = MarkdownxField(
        _("uiterste termijn"),
        help_text=_(
            "Deadlines.",
        ),
        blank=True,
        null=True,
    )
    wtd_bij_geen_reactie = MarkdownxField(
        _("wtd bij geen reactie"),
        help_text=_(
            "Wat te doen bij geen reactie.",
        ),
        blank=True,
        null=True,
    )
    decentrale_procedure_link = models.URLField(
        _("decentrale procedure link"),
        help_text=_("Link naar de procedure voor burgers en / of bedrijven."),
        blank=True,
        null=True,
    )

    def get_fields(self):
        return [
            (
                f.verbose_name,
                f.value_from_object(self),
                f.help_text,
                type(f) == MarkdownxField,
            )
            for f in self.__class__._meta.fields
        ]

    def __str__(self):
        return f"{self.product_titel_decentraal}"

    class Meta:
        abstract = True

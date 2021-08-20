from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField


class ProductGegevensMixin(models.Model):
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

    class Meta:
        abstract = True


class ProductAanvraagGegevensMixin(models.Model):
    procedure_beschrijving = MarkdownxField(
        _("procedure beschrijving"),
        help_text=_(
            "Procedurebeschrijving.",
        ),
    )
    vereisten = MarkdownxField(
        _("vereisten"),
        help_text=_(
            "Vereisten auth/id/sign.",
        ),
    )
    bewijs = MarkdownxField(
        _("bewijs"),
        help_text=_(
            "Bewijs (type/format).",
        ),
    )
    bezwaar_en_beroep = MarkdownxField(
        _("bezwaar en beroep"),
        help_text=_(
            "Bezwaar en beroep.",
        ),
    )
    kosten_en_betaalmethoden = MarkdownxField(
        _("kosten en betaalmethoden"),
        help_text=_(
            "Kosten en betaalmethoden.",
        ),
    )
    uiterste_termijn = MarkdownxField(
        _("uiterste termijn"),
        help_text=_(
            "Deadlines.",
        ),
    )
    wtd_bij_geen_reactie = MarkdownxField(
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
        abstract = True


class ContactgegevensMixin(models.Model):
    contact_naam = models.CharField(
        _("contact naam"),
        max_length=40,
        help_text=_("De naam van de verantwoordelijke contactpersoon."),
    )
    contact_website = models.URLField(
        _("contact website"),
        blank=True,
        null=True,
        help_text=_("De website van de verantwoordelijke contactpersoon."),
    )
    contact_telefoonnummer = models.CharField(
        _("contact telefoonnummer"),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Het telefoonnummer van de verantwoordelijke contactpersoon."),
    )
    contact_emailadres = models.EmailField(
        _("contact emailadres"),
        max_length=254,
        blank=True,
        null=True,
        help_text=_("Het e-mailadres van de verantwoordelijke contactpersoon."),
    )

    class Meta:
        abstract = True

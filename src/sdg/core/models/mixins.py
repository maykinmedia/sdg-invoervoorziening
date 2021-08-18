from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField


class ProductGegevensMixin(models.Model):
    product_titel_decentraal = models.CharField(
        _("product titel decentraal"),
        max_length=50,
        help_text=_(
            "De titel van het decentrale product, die immers kan afwijken van de landelijke titel."
        ),
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
            "Decentrale overheden geven een wijzigingsdatum mee voor hun informatie. Deze datum wordt op het portaal "
            "getoond. "
        ),
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

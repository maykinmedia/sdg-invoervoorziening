from abc import ABC
from typing import Any, List, Tuple

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.producten.utils import ProductField


class BaseGegevensMixin(models.Model):
    def _get_field_value(self, field) -> Tuple[Any, bool]:
        """Get the value of a field. If empty, retrieve from standard.

        :return: The field value, whether it is standard or not.
        """
        value = field.value_from_object(self)

        if not value and getattr(self, "standaard", None):
            # TODO: Revise getattr
            return getattr(self.standaard, field.name, None), True

        return value, False

    def _get_field(self, field) -> ProductField:
        """Gets field specific information."""
        if isinstance(field, str):
            field = self.__class__._meta.get_field(field)

        value, is_standard = self._get_field_value(field)
        return ProductField(
            name=field.verbose_name,
            value=value,
            help_text=field.help_text,
            is_standard=is_standard,
            is_markdown=type(field) == MarkdownxField,
        )

    def get_fields(self) -> List[ProductField]:
        """Returns data for each field as a list of Field objects."""
        return [self._get_field(field) for field in self.__class__._meta.fields]

    def get_field(self, field) -> ProductField:
        """Returns data for a single field."""
        return self._get_field(field)

    class Meta:
        abstract = True


class ProductGegevensMixin(BaseGegevensMixin):
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

    def __str__(self):
        return f"{self.product_titel_decentraal}"

    class Meta:
        abstract = True


class ProductAanvraagGegevensMixin(BaseGegevensMixin):
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

from typing import Any, List, Tuple

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from markdownx.models import MarkdownxField

from sdg.core.constants import TaalChoices
from sdg.producten.utils import ProductField


class ProductFieldMixin:
    def _get_field_value(self, field) -> Tuple[Any, bool]:
        """Get the value of a field. If empty, retrieve from standard.

        :return: The field value, whether it is standard or not.
        """
        value = field.value_from_object(self)

        if not value and getattr(self, "specifiek_product", None):
            # TODO: optimize and refactor after major changes [issue #80]
            try:
                referentie_info = self.specifiek_product.referentie.informatie.get(
                    taal=self.taal,
                )
            except ObjectDoesNotExist:
                return None, True
            return getattr(referentie_info, field.name, None), True

        return value, False

    def _get_field(self, field) -> ProductField:
        """Gets field specific information."""
        if isinstance(field, str):
            field = self.__class__._meta.get_field(field)
        value, is_reference = self._get_field_value(field)
        return ProductField(
            name=field.name,
            verbose_name=field.verbose_name,
            value=value,
            help_text=field.help_text,
            is_reference=is_reference,
            is_markdown=type(field) == MarkdownxField,
        )

    def get_fields(self) -> List[ProductField]:
        """Returns data for each field as a list of Field objects."""
        all_fields = self.__class__._meta.fields
        return [self._get_field(field) for field in all_fields]

    def get_field(self, field) -> ProductField:
        """Returns data for a single field."""
        return self._get_field(field)


class GeneriekProductGegevensMixin(ProductFieldMixin, models.Model):
    taal = models.CharField(
        _("taal"),
        choices=TaalChoices.choices,
        max_length=32,
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

    def __str__(self):
        return f"{self.product_titel_decentraal}"

    class Meta:
        abstract = True


class ProductGegevensMixin(ProductFieldMixin, models.Model):
    taal = models.CharField(
        _("taal"),
        choices=TaalChoices.choices,
        max_length=32,
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

    def __str__(self):
        return f"{self.product_titel_decentraal}"

    class Meta:
        abstract = True

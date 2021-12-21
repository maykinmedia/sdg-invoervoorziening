from typing import Any, List, Tuple

from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.constants import TaalChoices
from sdg.producten.types import ProductFieldInfo


class ProductFieldMixin:
    def _get_field_value(self, field) -> Tuple[Any, bool]:
        """Get the value of a field. If empty, retrieve from standard.

        :return: The field value, whether it is standard or not.
        """
        value = field.value_from_object(self)

        if not value and hasattr(self, "referentie_informatie"):
            return getattr(self.referentie_informatie, field.name, ""), True

        return value, False

    def _get_field(self, field) -> ProductFieldInfo:
        """Gets field specific information for products."""
        if isinstance(field, str):
            field = self.__class__._meta.get_field(field)
        value, is_reference = self._get_field_value(field)
        return ProductFieldInfo(
            name=field.name,
            verbose_name=field.verbose_name,
            value=value,
            help_text=field.help_text,
            is_reference=is_reference,
            type=field.get_internal_type(),
        )

    def get_fields(self) -> List[ProductFieldInfo]:
        """Returns data for each field as a list of Field objects."""
        all_fields = self.__class__._meta.fields
        return [self._get_field(field) for field in all_fields]

    def get_field(self, field) -> ProductFieldInfo:
        """Returns data for a single field."""
        return self._get_field(field)


class TaalMixin(models.Model):
    taal = models.CharField(
        _("taal"),
        choices=TaalChoices.choices,
        max_length=2,
        help_text=_(
            "De taal waarin de betreffende tekst is geschreven."
            "ISO 639-1 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)"
        ),
    )

    class Meta:
        abstract = True

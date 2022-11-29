from typing import List

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from sdg.core.constants import TaalChoices
from sdg.core.models.mixins import FieldConfigurationMixin
from sdg.core.types import LabeledTooltip
from sdg.producten.types import ProductFieldMetadata


class ProductFieldMixin(FieldConfigurationMixin):
    def _get_field(self, field) -> ProductFieldMetadata:
        """Gets field specific information for products."""
        if isinstance(field, str):
            field = self._meta.get_field(field)
            try:
                language = self._meta.get_field("taal").value_from_object(self)
            except FieldDoesNotExist:
                language = "default"

        if self.configuration and field:
            field_config = self.configuration[language].for_field(
                prefix=self._meta.model_name,
                name=field.name,
                default=LabeledTooltip(
                    label=field.verbose_name, tooltip=field.help_text
                ),
            )

            return ProductFieldMetadata(
                name=field.name,
                verbose_name=field.verbose_name,
                value=field.value_from_object(self),
                help_text=field.help_text,
                type=field.get_internal_type(),
                configuration=field_config,
            )

    def get_fields(self, fields=None) -> List[ProductFieldMetadata]:
        """Returns data for each field as a list of Field objects."""
        if not fields:
            fields = self.__class__._meta.fields

        return [self._get_field(field) for field in fields]

    def get_field(self, field) -> ProductFieldMetadata:
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

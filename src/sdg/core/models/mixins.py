from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.models import ProductFieldConfiguration


class FieldConfigurationMixin:
    _configuration: ProductFieldConfiguration = None

    @property
    def configuration(self):
        if self._configuration is None:
            self._configuration = ProductFieldConfiguration.get_solo()
        return self._configuration

    def configure_fields(self):
        model_meta = self._meta.model._meta
        model = model_meta.model_name

        for name, field in self.fields.items():
            try:
                field.help_text = model_meta.get_field(field).help_text
            except FieldDoesNotExist:
                pass
            if configuration := self.configuration.for_field(prefix=model, name=name):
                field.label, field.help_text = configuration[0]

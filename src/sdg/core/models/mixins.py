from django.core.exceptions import FieldDoesNotExist

from sdg.core.models import ProductFieldConfiguration


class FieldConfigurationMixin:
    _configuration: ProductFieldConfiguration = None

    @property
    def configuration(self):
        if self._configuration is None:
            config = ProductFieldConfiguration.get_solo()
            self._configuration = {
                "default": config,
                "nl": config.localizedproductfieldconfiguration_set.get(taal="nl"),
                "en": config.localizedproductfieldconfiguration_set.get(taal="en"),
            }
        return self._configuration

    def configure_fields(self, taal=""):
        model_meta = self._meta.model._meta
        model = model_meta.model_name

        for name, field in self.fields.items():
            try:
                field.help_text = model_meta.get_field(field).help_text
            except FieldDoesNotExist:
                pass

            if taal:
                configuration = self.configuration[taal].for_field(
                    prefix=model, name=name
                )
            else:
                configuration = self.configuration["default"].for_field(
                    prefix=model, name=name
                )

            if configuration and len(configuration[0]) == 2:
                field.label, field.help_text = configuration[0]

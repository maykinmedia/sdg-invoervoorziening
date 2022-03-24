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

    def configure_field_text(self):
        model_meta = self._meta.model._meta
        model = model_meta.model_name

        for name, field in self.fields.items():
            if configuration := self.configuration.for_field(prefix=model, name=name):
                field.label, field.help_text = configuration[0]
            try:
                self.fields[name].help_text = model_meta.get_field(field).help_text
            except FieldDoesNotExist:
                pass


class ContactgegevensMixin(models.Model):
    contact_naam = models.CharField(
        _("contact naam"),
        max_length=40,
        help_text=_("de naam van de verantwoordelijke contactpersoon."),
    )
    contact_website = models.URLField(
        _("contact website"),
        blank=True,
        help_text=_("Website van de gemeente."),
    )
    contact_telefoonnummer = models.CharField(
        _("contact telefoonnummer"),
        max_length=20,
        blank=True,
        help_text=_("Het telefoonnummer van de gemeente."),
    )
    contact_emailadres = models.EmailField(
        _("contact emailadres"),
        max_length=254,
        blank=True,
        help_text=_("Het e-mailadres van de verantwoordelijke contactpersoon."),
    )

    class Meta:
        abstract = True

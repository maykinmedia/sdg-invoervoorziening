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

    def __getitem__(self, name):
        item = super().__getitem__(name)
        if not getattr(item, "configuration", None):
            item.configuration = self.configuration.for_field(
                prefix=self._meta.model._meta.model_name,
                name=name,
            )
        return item


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

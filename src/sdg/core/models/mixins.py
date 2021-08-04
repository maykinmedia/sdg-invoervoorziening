from django.db import models
from django.utils.translation import ugettext_lazy as _


class ContactgegevensMixin(models.Model):
    contact_naam = models.CharField(
        _("contact naam"),
        max_length=40,
        help_text=_("De naam van de verantwoordelijke contactpersoon."),
    )
    contact_website = models.URLField(
        _("contact website"),
        blank=True, null=True,
        help_text=_("De website van de verantwoordelijke contactpersoon."),
    )
    contact_telefoonnummer = models.CharField(
        _("contact telefoonnummer"),
        max_length=20,
        blank=True, null=True,
        help_text=_("Het telefoonnummer van de verantwoordelijke contactpersoon."),
    )
    contact_emailadres = models.EmailField(
        _("contact emailadres"),
        max_length=254,
        blank=True, null=True,
        help_text=_("Het e-mailadres van de verantwoordelijke contactpersoon."),
    )

    class Meta:
        abstract = True

    def publish(self):
        self.concept = False
        self.save()

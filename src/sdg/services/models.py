from typing import Dict, List

from django.db import models
from django.utils.translation import ugettext_lazy as _

from zgw_consumers.models import Service

from sdg.core.constants import DoelgroepChoices


class ServiceConfiguration(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    doelgroep = models.CharField(
        max_length=32,
        choices=DoelgroepChoices.choices,
        help_text=_("De doelgroep waarvoor deze service is geconfigureerd. "),
    )

    def retrieve_products(self) -> List[Dict]:
        """
        Fetch products according to the configured API.
        """
        client = self.service.build_client()
        return client.retrieve_products()

    class Meta:
        verbose_name = _("Serviceconfiguratie")
        verbose_name_plural = _("Serviceconfiguraties")
        constraints = [
            models.UniqueConstraint(
                fields=["service", "doelgroep"],
                name="unique_service_configuration",
            )
        ]

    def __str__(self):
        return f"{self.service.label} — {self.doelgroep}"

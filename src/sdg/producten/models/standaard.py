from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sdg.producten.models.mixins import (
    ProductAanvraagGegevensMixin,
    ProductGegevensMixin,
)


class StandaardProductSpecifiekInformatie(ProductGegevensMixin, models.Model):
    """Standaardinformatie voor ProductSpecifiekInformatie."""

    def get_absolute_url(self):
        return reverse("producten:detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("standaard product specifiek informatie")
        verbose_name_plural = _("standaard product specifiek informatie")


class StandaardProductSpecifiekAanvraag(ProductAanvraagGegevensMixin, models.Model):
    """Standaardinformatie voor ProductSpecifiekAanvraag."""

    class Meta:
        verbose_name = _("standaard product specifiek aanvraag")
        verbose_name_plural = _("standaard product specifiek aanvragen")


class StandaardProductuitvoering(ProductGegevensMixin, models.Model):
    """Standaardinformatie voor Productuitvoering."""

    class Meta:
        verbose_name = _("standaard productuitvoering")
        verbose_name_plural = _("standaard productuitvoeringen")

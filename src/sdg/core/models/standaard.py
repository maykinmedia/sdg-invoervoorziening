from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.models.mixins import ProductAanvraagGegevensMixin, ProductGegevensMixin


class StandaardProductSpecifiekInformatie(ProductGegevensMixin, models.Model):
    """Standaardinformatie voor ProductSpecifiekInformatie."""

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

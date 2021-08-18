from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.models.mixins import ContactgegevensMixin


class LokaleOverheid(ContactgegevensMixin, models.Model):
    ondersteunings_organisatie = models.ForeignKey(
        "Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("ondersteunings organisatie"),
        help_text=_("Organisatie voor ondersteuning."),
        related_name="ondersteunings",
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de decentrale informatie."),
        related_name="verantwoordelijke",
    )
    bevoegde_organisatie = models.ForeignKey(
        "Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("bevoegde organisatie"),
        help_text=_("Bevoegd gezag verantwoordelijk voor de procedure."),
        related_name="bevoegde",
    )

    class Meta:
        verbose_name = _("lokale overheid")
        verbose_name_plural = _("lokale overheden")


class Lokatie(models.Model):
    lokale_overheid = models.ForeignKey(
        "LokaleOverheid",
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
    )
    product = models.ForeignKey(
        "ProductSpecifiekAanvraag",
        on_delete=models.PROTECT,
        verbose_name=_("product"),
    )

    lokatie_adres = models.TextField(
        _("lokatie adres"),
        max_length=1000,
        help_text=_("De gegevens over het adres van de lokatie."),
    )

    class Meta:
        verbose_name = _("lokatie")
        verbose_name_plural = _("lokaties")

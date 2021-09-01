from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sdg.core.models.mixins import ContactgegevensMixin
from sdg.core.models.validators import validate_lau

User = get_user_model()


class LokaleOverheid(ContactgegevensMixin, models.Model):
    ondersteunings_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("ondersteunings organisatie"),
        help_text=_("Organisatie voor ondersteuning."),
        related_name="ondersteunings",
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de decentrale informatie."),
        related_name="verantwoordelijke",
    )
    bevoegde_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("bevoegde organisatie"),
        help_text=_("Bevoegd gezag verantwoordelijk voor de procedure."),
        related_name="bevoegde",
    )
    organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("organisatie"),
        help_text=_("De organisatie van de lokale overheid."),
        related_name="organisatie",
    )
    lau_code = models.CharField(
        _("LAU-code"),
        blank=True,
        null=True,
        max_length=5,
        validators=[validate_lau],
        help_text=_("Een geldige LAU-code van de organisatie."),
    )
    users = models.ManyToManyField(User, through="accounts.Role")

    def get_absolute_url(self):
        return reverse("organisaties:overheid_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.organisatie.owms_pref_label

    class Meta:
        verbose_name = _("lokale overheid")
        verbose_name_plural = _("lokale overheden")


class Lokatie(models.Model):
    lokale_overheid = models.ForeignKey(
        "LokaleOverheid",
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
        related_name="lokaties",
    )

    naam = models.CharField(
        _("naam"),
        max_length=40,
        help_text=_("De naam van de lokatie."),
    )
    lokatie_adres = models.TextField(  # TODO: Rename field to 'adres' if approved
        _("lokatie adres"),
        max_length=1000,
        help_text=_("De gegevens over het adres van de lokatie."),
    )

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _("lokatie")
        verbose_name_plural = _("lokaties")

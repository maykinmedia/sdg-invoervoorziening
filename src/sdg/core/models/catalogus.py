from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from sdg.accounts.models import Role
from sdg.core.models.validators import (
    validate_reference_catalog,
    validate_specific_catalog,
    validate_uppercase,
)

User = get_user_model()


class ProductenCatalogus(models.Model):
    referentie_catalogus = models.ForeignKey(
        "self",
        verbose_name=_("referentie catalogus"),
        related_name="specifieke_catalogi",
        help_text=_("De catalogus van referentie."),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    lokale_overheid = models.ForeignKey(
        "organisaties.LokaleOverheid",
        verbose_name=_("lokale overheid"),
        help_text=_("De lokale overheid die bij deze catalogus hoort."),
        related_name="catalogi",
        on_delete=models.CASCADE,
    )
    is_referentie_catalogus = models.BooleanField(
        _("is referentie catalogus"),
        default=False,
        help_text=_("Geeft aan of dit een referentiecatalogus is."),
    )
    domein = models.CharField(
        _("domein"),
        max_length=5,
        validators=[validate_uppercase],
        help_text=_("Een afkorting die wordt gebruikt om het domein aan te duiden."),
    )
    versie = models.PositiveIntegerField(
        default=1,
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het producten catalogus."),
    )
    naam = models.CharField(
        _("naam"),
        max_length=40,
        help_text=_("De naam van de producten catalogus."),
    )
    toelichting = models.TextField(
        _("toelichting"), blank=True, help_text="Toelichting bij het catalogus."
    )

    @property
    def verantwoordelijke_organisatie(self):
        """The department that is responsible (co-management products), e.g. BZK for passport; "municipalities" for
        autonomous products (e.g. terrace permit)"""

        return self.lokale_overheid.verantwoordelijke_organisatie

    def user_is_redacteur(self, user: User) -> bool:
        role = get_object_or_404(Role, user=user, lokale_overheid=self.lokale_overheid)
        if role.is_redacteur:
            return True
        else:
            return False

    def has_reference_catalog(self) -> bool:
        """Returns whether this catalog has a reference catalog."""
        return bool(self.referentie_catalogus)

    def __str__(self):
        if self.is_referentie_catalogus:
            return f"{self.naam} (referentie)"
        else:
            return f"{self.naam}"

    class Meta:
        verbose_name = _("producten catalogus")
        verbose_name_plural = _("producten catalogi")
        constraints = [
            models.UniqueConstraint(
                fields=["referentie_catalogus", "lokale_overheid"],
                name="unique_referentie_catalogus_and_lokale_overheid",
            )
        ]

    def clean(self):
        super().clean()

        if self.is_referentie_catalogus:
            validate_reference_catalog(self)
        else:
            validate_specific_catalog(self)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.models.validators import validate_uppercase


class ProductenCatalogus(models.Model):
    referentie_catalogus = models.ForeignKey(
        "self",
        verbose_name=_("referentie catalogus"),
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
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
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
        """Het departement dat verantwoordelijk is (medebewind producten), bv BZK voor paspoort; "gemeenten" voor
        autonome producten (bv terrasvergunning)"""
        return self.lokale_overheid.verantwoordelijke_organisatie

    def __str__(self):
        return f"{self.naam} - {self.versie}"

    class Meta:
        verbose_name = _("producten catalogus")
        verbose_name_plural = _("productcatalogi")

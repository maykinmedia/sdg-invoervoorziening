from django.db import models
from django.utils.translation import ugettext_lazy as _

from .mixins import ContactgegevensMixin


class Overheidsorganisatie(ContactgegevensMixin, models.Model):
    owms_identifier = models.URLField(
        _("owms identifier"),
        help_text=_(
            "De metadatastandaard voor informatie van de nederlandse overheid op internet."
        ),
    )
    owms_pref_label = models.CharField(
        _("owms pref label"),
        max_length=80,
        help_text=_("De wettelijk erkende naam van de organisatie."),
    )
    naam = models.CharField(
        _("naam"),
        max_length=40,
        help_text=_("De naam van de overheidsorganisatie."),
    )

    def __str__(self):
        return f"{self.owms_identifier} - {self.owms_pref_label}"

    class Meta:
        verbose_name = _("overheidsorganisatie")
        verbose_name_plural = _("overheidsorganisaties")


class Informatiegebied(models.Model):
    code = models.CharField(
        _("code"),
        max_length=3,
        help_text=_("De code van het desbetreffende informatiegebied."),
    )
    informatiegebied = models.CharField(
        _("informatiegebied"),
        max_length=40,
        help_text=_("Het bij de gegevens behorende informatiegebied."),
    )

    def __str__(self):
        return f"{self.informatiegebied} [{self.code}]"

    class Meta:
        verbose_name = _("informatiegebied")
        verbose_name_plural = _("informatiegebieden")


class Thema(models.Model):
    informatiegebied = models.OneToOneField(
        "Informatiegebied",
        on_delete=models.PROTECT,
        related_name="thema",
        verbose_name=_("informatiegebied"),
        help_text=_("Het informatiegebied met betrekking tot dit thema."),
    )
    code = models.CharField(
        _("code"),
        max_length=3,
        help_text=_("De code van het desbetreffende thema."),
    )
    thema = models.CharField(
        _("thema"),
        max_length=40,
        help_text=_("Het thema dat verband houdt met de gegevens."),
    )

    def __str__(self):
        return f"{self.thema} [{self.code}]"

    class Meta:
        verbose_name = _("thema")
        verbose_name_plural = _("thema's")


class UniformeProductnaam(models.Model):
    thema = models.ForeignKey(
        "Thema",
        on_delete=models.PROTECT,
        related_name="upn",
        verbose_name=_("thema"),
        help_text=_("Het informatiegebied met betrekking tot dit thema."),
    )
    upn_uri = models.URLField(
        _("UPN URI"),
        help_text=_(
            "Uniforme Productnaam URI van landelijk product",
        ),
    )
    upn_label = models.CharField(
        _("UPN label"),
        max_length=255,
        help_text=_(
            "Het bijbehorende label. Zie https://standaarden.overheid.nl/owms/oquery/UPL-actueel.plain voor de "
            "volledige UPL. "
        ),
    )

    def __str__(self):
        return f"{self.upn_uri} - {self.upn_label}"

    class Meta:
        verbose_name = _("uniforme productnaam")
        verbose_name_plural = _("uniforme productnamen")

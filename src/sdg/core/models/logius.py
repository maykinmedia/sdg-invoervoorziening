from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.managers import OrganisatieManager


class Overheidsorganisatie(models.Model):
    owms_identifier = models.URLField(
        _("OWMS identifier"),
        help_text=_(
            "De metadatastandaard voor informatie van de nederlandse overheid op internet."
        ),
        unique=True,
    )
    owms_pref_label = models.CharField(
        _("OWMS pref label"),
        max_length=80,
        help_text=_("De wettelijk erkende naam van de organisatie."),
    )
    owms_end_date = models.DateTimeField(
        _("end date"),
        help_text=_("De endDate, zoals gevonden in het OWMS-model."),
        blank=True,
        null=True,
    )

    objects = OrganisatieManager()

    def __str__(self):
        return self.owms_pref_label

    class Meta:
        verbose_name = _("overheidsorganisatie")
        verbose_name_plural = _("overheidsorganisaties")


class Informatiegebied(models.Model):
    code = models.CharField(
        _("code"),
        max_length=3,
        help_text=_("De code van het desbetreffende informatiegebied."),
        unique=True,
    )
    informatiegebied = models.CharField(
        _("informatiegebied"),
        max_length=80,
        help_text=_("Het bij de gegevens behorende informatiegebied."),
    )
    informatiegebied_uri = models.URLField(
        _("informatiegebied uri"),
        help_text=_(
            "Informatiegebied URI van landelijk product",
        ),
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
    thema = models.CharField(
        _("thema"),
        max_length=512,
        help_text=_("Het thema dat verband houdt met de gegevens."),
    )
    thema_uri = models.URLField(
        _("thema uri"),
        help_text=_(
            "Thema URI van landelijk product",
        ),
    )

    @property
    def code(self):
        return self.informatiegebied.code

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
        blank=True,
        null=True,
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

    rijk = models.BooleanField(
        _("rijk"),
        default=False,
    )
    provincie = models.BooleanField(
        _("provincie"),
        default=False,
    )
    waterschap = models.BooleanField(
        _("waterschap"),
        default=False,
    )
    gemeente = models.BooleanField(
        _("gemeente"),
        default=False,
    )
    burger = models.BooleanField(
        _("burger"),
        default=False,
    )
    bedrijf = models.BooleanField(
        _("bedrijf"),
        default=False,
    )
    dienstenwet = models.BooleanField(
        _("dienstenwet"),
        default=False,
    )
    sdg = models.BooleanField(
        _("sdg"),
        default=False,
    )
    autonomie = models.BooleanField(
        _("autonomie"),
        default=False,
    )
    medebewind = models.BooleanField(
        _("medebewind"),
        default=False,
    )
    aanvraag = models.BooleanField(
        _("aanvraag"),
        default=False,
    )
    subsidie = models.BooleanField(
        _("subsidie"),
        default=False,
    )
    melding = models.BooleanField(
        _("melding"),
        default=False,
    )
    verplichting = models.BooleanField(
        _("verplichting"),
        default=False,
    )
    digi_d_macht = models.BooleanField(
        _("digi_d_macht"),
        default=False,
    )

    grondslag = models.CharField(
        _("grondslag"),
        blank=True,
        null=True,
        max_length=80,
    )
    grondslaglabel = models.CharField(
        _("grondslaglabel"),
        blank=True,
        null=True,
        max_length=512,
    )
    grondslaglink = models.URLField(
        _("grondslaglink"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.upn_uri} - {self.upn_label}"

    class Meta:
        verbose_name = _("uniforme productnaam")
        verbose_name_plural = _("uniforme productnamen")

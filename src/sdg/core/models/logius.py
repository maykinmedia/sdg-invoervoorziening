from typing import Set

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from sdg.core.models.managers import OrganisatieQuerySet


class Overheidsorganisatie(models.Model):
    """
    Government organization
    """

    owms_identifier = models.URLField(
        _("OWMS identificatie"),
        help_text=_(
            "De metadatastandaard voor informatie van de nederlandse overheid op internet."
        ),
        unique=True,
    )
    owms_pref_label = models.CharField(
        _("OWMS label"),
        max_length=200,
        help_text=_("De wettelijk erkende naam van de organisatie."),
    )
    owms_end_date = models.DateTimeField(
        _("einddatum"),
        help_text=_("De einddatum, zoals gevonden in het OWMS-model."),
        blank=True,
        null=True,
    )

    objects = OrganisatieQuerySet.as_manager()

    class Meta:
        verbose_name = _("overheidsorganisatie")
        verbose_name_plural = _("overheidsorganisaties")

    def __str__(self):
        if self.owms_end_date:
            return _("{label} (opgeheven op {end_date})").format(
                label=self.owms_pref_label,
                end_date=self.owms_end_date.date(),
            )
        return self.owms_pref_label


class Informatiegebied(models.Model):
    """
    Information area
    """

    informatiegebied = models.CharField(
        _("informatiegebied"),
        max_length=80,
        help_text=_("Het bij de gegevens behorende SDG informatiegebied."),
    )
    informatiegebied_uri = models.URLField(
        _("informatiegebied URI"),
        help_text=_(
            "Informatiegebied SDG URI van landelijk product",
        ),
        unique=True,
    )

    class Meta:
        verbose_name = _("informatiegebied")
        verbose_name_plural = _("informatiegebieden")

    def __str__(self):
        return f"{self.informatiegebied}"


class Thema(models.Model):
    """
    Theme
    """

    code = models.CharField(
        _("code"),
        max_length=32,
        help_text=_("De SDG code van het desbetreffende informatiegebied."),
        unique=True,
    )
    informatiegebied = models.ForeignKey(
        "Informatiegebied",
        on_delete=models.PROTECT,
        related_name="thema",
        verbose_name=_("informatiegebied"),
        help_text=_("Het informatiegebied met betrekking tot dit thema."),
    )
    thema = models.CharField(
        _("thema"),
        max_length=512,
        help_text=_("Het SDG thema dat verband houdt met de gegevens."),
    )
    thema_uri = models.URLField(
        _("thema uri"),
        help_text=_(
            "SDG thema URI van landelijk product",
        ),
        unique=True,
    )

    class Meta:
        verbose_name = _("thema")
        verbose_name_plural = _("thema's")

    def __str__(self):
        return f"{self.thema}"


class UniformeProductnaam(models.Model):
    """
    UPN

    The base for every product.
    """

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
        unique=True,
    )
    upn_label = models.CharField(
        _("UPN label"),
        max_length=255,
        help_text=_(
            "Het bijbehorende label. Zie https://standaarden.overheid.nl/owms/oquery/UPL-actueel.plain voor de "
            "volledige UPL. "
        ),
    )

    # There can be several "grondslagen" (legal basis) for a UPN. The
    # representation on standaarden.overheid.nl is flattened. For the sake of
    # the UPN URI and UPN label, we don't need these fields at the moment nor
    # their differences for each layer of government. The boolean fields below
    # already reflect that they can be used by several layers of government.
    rijk = models.BooleanField(_("rijk"), default=False)
    provincie = models.BooleanField(_("provincie"), default=False)
    waterschap = models.BooleanField(_("waterschap"), default=False)
    gemeente = models.BooleanField(_("gemeente"), default=False)
    burger = models.BooleanField(_("burger"), default=False)
    bedrijf = models.BooleanField(_("bedrijf"), default=False)
    dienstenwet = models.BooleanField(_("dienstenwet"), default=False)
    autonomie = models.BooleanField(_("autonomie"), default=False)
    medebewind = models.BooleanField(_("medebewind"), default=False)
    aanvraag = models.BooleanField(_("aanvraag"), default=False)
    subsidie = models.BooleanField(_("subsidie"), default=False)
    melding = models.BooleanField(_("melding"), default=False)
    verplichting = models.BooleanField(_("verplichting"), default=False)
    digi_d_macht = models.BooleanField(_("digi_d_macht"), default=False)
    sdg = ArrayField(
        verbose_name=_("sdg"),
        base_field=models.CharField(max_length=4),
        blank=True,
        default=list,
    )

    def get_active_fields(self) -> Set[str]:
        """:returns: A set of active boolean field names for this UPN."""

        def _is_active_field(field):
            if isinstance(field, models.BooleanField) or field.name == "sdg":
                return getattr(self, field.name, False)

        return {
            field.name for field in self._meta.get_fields() if _is_active_field(field)
        }

    class Meta:
        verbose_name = _("uniforme productnaam")
        verbose_name_plural = _("uniforme productnamen")

    def __str__(self):
        return self.upn_label

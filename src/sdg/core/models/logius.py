from django.db import models
from django.utils.translation import ugettext_lazy as _

from sdg.core.managers import OrganisatieManager
from sdg.core.models import ProductenCatalogus
from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)


class Overheidsorganisatie(models.Model):
    """
    Government organization
    """

    owms_identifier = models.URLField(
        _("OWMS identifier"),
        help_text=_(
            "De metadatastandaard voor informatie van de nederlandse overheid op internet."
        ),
        unique=True,
    )
    owms_pref_label = models.CharField(
        _("OWMS pref label"),
        max_length=200,
        help_text=_("De wettelijk erkende naam van de organisatie."),
    )
    owms_end_date = models.DateTimeField(
        _("end date"),
        help_text=_("De endDate, zoals gevonden in het OWMS-model."),
        blank=True,
        null=True,
    )

    objects = OrganisatieManager()

    class Meta:
        verbose_name = _("overheidsorganisatie")
        verbose_name_plural = _("overheidsorganisaties")

    def __str__(self):
        return self.owms_pref_label


class Informatiegebied(models.Model):
    """
    Information area
    """

    code = models.CharField(
        _("code"),
        max_length=32,
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

    class Meta:
        verbose_name = _("informatiegebied")
        verbose_name_plural = _("informatiegebieden")

    def __str__(self):
        return f"{self.informatiegebied} [{self.code}]"


class Thema(models.Model):
    """
    Theme
    """

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
        help_text=_("Het thema dat verband houdt met de gegevens."),
    )
    thema_uri = models.URLField(
        _("thema uri"),
        help_text=_(
            "Thema URI van landelijk product",
        ),
        unique=True,
    )

    @property
    def code(self):
        return self.informatiegebied.code

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
    )
    upn_label = models.CharField(
        _("UPN label"),
        max_length=255,
        help_text=_(
            "Het bijbehorende label. Zie https://standaarden.overheid.nl/owms/oquery/UPL-actueel.plain voor de "
            "volledige UPL. "
        ),
    )

    rijk = models.BooleanField(_("rijk"), default=False)
    provincie = models.BooleanField(_("provincie"), default=False)
    waterschap = models.BooleanField(_("waterschap"), default=False)
    gemeente = models.BooleanField(_("gemeente"), default=False)
    burger = models.BooleanField(_("burger"), default=False)
    bedrijf = models.BooleanField(_("bedrijf"), default=False)
    dienstenwet = models.BooleanField(_("dienstenwet"), default=False)
    sdg = models.BooleanField(_("sdg"), default=False)
    autonomie = models.BooleanField(_("autonomie"), default=False)
    medebewind = models.BooleanField(_("medebewind"), default=False)
    aanvraag = models.BooleanField(_("aanvraag"), default=False)
    subsidie = models.BooleanField(_("subsidie"), default=False)
    melding = models.BooleanField(_("melding"), default=False)
    verplichting = models.BooleanField(_("verplichting"), default=False)
    digi_d_macht = models.BooleanField(_("digi_d_macht"), default=False)

    grondslag = models.CharField(
        _("grondslag"),
        blank=True,
        max_length=80,
    )
    grondslaglabel = models.CharField(
        _("grondslaglabel"),
        blank=True,
        max_length=512,
    )
    grondslaglink = models.URLField(
        _("grondslaglink"),
        blank=True,
    )

    def generate_initial_data(self, catalog: ProductenCatalogus):
        generic = GeneriekProduct.objects.create(upn=self)

        product = Product.objects.create(generiek_product=generic, catalogus=catalog)
        LocalizedGeneriekProduct.objects.localize(
            instance=generic, languages=["nl", "en"]
        )

        version = ProductVersie.objects.create(product=product, publicatie_datum=None)
        LocalizedProduct.objects.localize(instance=version, languages=["nl", "en"])

    class Meta:
        verbose_name = _("uniforme productnaam")
        verbose_name_plural = _("uniforme productnamen")
        constraints = [
            models.UniqueConstraint(
                fields=["upn_uri", "grondslag"], name="unique_upn_uri_and_grondslag"
            )
        ]

    def __str__(self):
        return self.upn_label

    def save(self, *args, **kwargs):
        adding = self._state.adding
        super().save(*args, **kwargs)

        if adding:
            for catalog in ProductenCatalogus.objects.filter(
                autofill=True, is_referentie_catalogus=True
            ):
                if all(f in self.upn_label for f in catalog.autofill_upn_filter):
                    self.generate_initial_data(catalog)

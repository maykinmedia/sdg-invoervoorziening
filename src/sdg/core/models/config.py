import datetime
from functools import partial

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

from sdg.core.db.fields import DynamicArrayField
from sdg.core.forms import LabeledTooltipWidget
from sdg.core.models.base import ProductFieldConfigurationMixin
from sdg.core.models.validators import DomainValidator

LabeledTooltipField = partial(
    DynamicArrayField,
    base_field=ArrayField(
        models.CharField(max_length=512),
    ),
    subwidget_form=LabeledTooltipWidget,
    blank=True,
    default=list,
)


class ProductFieldConfiguration(
    ProductFieldConfigurationMixin,
    SingletonModel,
):
    product_product_aanwezig = LabeledTooltipField(
        verbose_name=_("Product aanwezig"),
    )
    product_product_valt_onder = LabeledTooltipField(
        verbose_name=_("Product valt onder"),
    )
    product_bevoegde_organisatie = LabeledTooltipField(
        verbose_name=_("Bevoegde organisatie"),
    )
    product_locaties = LabeledTooltipField(
        verbose_name=_("Locaties"),
    )
    product_heeft_kosten = LabeledTooltipField(
        verbose_name=_("Heeft kosten"),
    )
    productversie_publicatie_datum = LabeledTooltipField(
        verbose_name=_("Publicatie datum"),
    )
    productversie_interne_opmerkingen = LabeledTooltipField(
        verbose_name=_("Interne opmerkingen"),
    )
    product_api_verborgen = LabeledTooltipField(
        verbose_name=_("Verborgen"),
    )
    product_automatisch_doordrukken = LabeledTooltipField(
        verbose_name=("Automatisch doordrukken"),
    )
    product_automatisch_doordrukken_datum = LabeledTooltipField(
        verbose_name=("Automatisch doordrukken datum"),
    )

    class Meta:
        verbose_name = _("Product field configuratie")
        verbose_name_plural = _("Product field configuratie")

    def __str__(self):
        return "Product field configuratie"


class SiteConfiguration(SingletonModel):
    """
    The global site configuration is used to modify customizable areas of
    the website, analytics, general settings, etc.
    """

    documentatie_titel = models.CharField(
        verbose_name=_("Documentatietitel"),
        help_text=_("De titel voor de documentatie link."),
        max_length=128,
        blank=True,
    )
    documentatie_link = models.URLField(
        verbose_name=_("Documentatielink"),
        help_text=_("Link naar de documentatie van de API."),
        blank=True,
    )

    goatcounter_domain = models.CharField(
        verbose_name=_("GoatCounter domain"),
        help_text=_(
            "Het domein waar goatcounter wordt gehost, bijvoorbeeld: example.com. Zorg ervoor dat het is toegestaan in het Content Security Policy als u het gebruikt."
        ),
        max_length=255,
        blank=True,
        validators=[
            DomainValidator(),
        ],
    )

    mail_text_changes_last_sent = models.DateField(
        verbose_name=_("Mail text changes last send"),
        help_text=_(
            "De aantal dagen since de laatse product update notificatie email task is getriggerd."
        ),
        default=datetime.date.today,
    )

    def __str__(self):
        return "Siteconfiguratie"

    class Meta:
        verbose_name = _("Siteconfiguratie")
        verbose_name_plural = _("Siteconfiguratie")

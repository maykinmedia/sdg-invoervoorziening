from functools import partial

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

from sdg.core.db.fields import DynamicArrayField
from sdg.core.forms import LabeledTooltipWidget

LabeledTooltipField = partial(
    DynamicArrayField,
    base_field=ArrayField(
        models.CharField(max_length=512),
    ),
    subwidget_form=LabeledTooltipWidget,
    blank=True,
    default=list,
)


class ProductFieldConfiguration(SingletonModel):
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
    productversie_publicatie_datum = LabeledTooltipField(
        verbose_name=_("Publicatie datum"),
    )

    def for_field(self, prefix, name):
        if name != "config":
            return getattr(self, "{}_{}".format(prefix, name), None)

    def __str__(self):
        return "Product field configuratie"

    class Meta:
        verbose_name = _("Product field configuratie")
        verbose_name_plural = _("Product field configuratie")

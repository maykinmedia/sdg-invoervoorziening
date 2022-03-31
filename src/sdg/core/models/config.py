from functools import partial

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

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
    """
    Configuration for the CMS product fields.
    Field format: [lowercase model]_[field]
    """

    product_product_aanwezig = LabeledTooltipField(
        verbose_name=_("Algemene aanwezigheid"),
    )
    product_product_aanwezig_toelichting = LabeledTooltipField(
        verbose_name=_("Algemene aanwezigheid toelichting"),
    )
    product_product_valt_onder = LabeledTooltipField(
        verbose_name=_("Algemene valt onder"),
    )
    product_bevoegde_organisatie = LabeledTooltipField(
        verbose_name=_("Algemene bevoegde organisatie"),
    )
    product_locaties = LabeledTooltipField(
        verbose_name=_("Algemene locaties"),
    )
    productversie_publicatie_datum = LabeledTooltipField(
        verbose_name=_("Algemene publicatie datum"),
    )

    localizedgeneriekproduct_product_titel = LabeledTooltipField(
        verbose_name=_("Generieke product titel"),
    )
    localizedgeneriekproduct_generieke_tekst = LabeledTooltipField(
        verbose_name=_("Generieke tekst"),
    )
    localizedgeneriekproduct_korte_omschrijving = LabeledTooltipField(
        verbose_name=_("Generieke korte omschrijving"),
    )
    localizedgeneriekproduct_datum_check = LabeledTooltipField(
        verbose_name=_("Generieke datum check"),
    )
    localizedgeneriekproduct_verwijzing_links = LabeledTooltipField(
        verbose_name=_("Generieke verwijzing links"),
    )
    localizedgeneriekproduct_landelijke_link = LabeledTooltipField(
        verbose_name=_("Generieke landelijke link"),
    )

    localizedproduct_product_titel_decentraal = LabeledTooltipField(
        verbose_name=_("Specifieke product titel decentraal"),
    )
    localizedproduct_specifieke_tekst = LabeledTooltipField(
        verbose_name=_("Specifieke tekst"),
    )
    localizedproduct_verwijzing_links = LabeledTooltipField(
        verbose_name=_("Specifieke verwijzing links"),
    )
    localizedproduct_decentrale_link = LabeledTooltipField(
        verbose_name=_("Specifieke decentrale link"),
    )
    localizedproduct_datum_wijziging = LabeledTooltipField(
        verbose_name=_("Specifieke datum wijziging"),
    )
    localizedproduct_procedure_beschrijving = LabeledTooltipField(
        verbose_name=_("Specifieke procedure beschrijving"),
    )
    localizedproduct_vereisten = LabeledTooltipField(
        verbose_name=_("Specifieke vereisten"),
    )
    localizedproduct_bewijs = LabeledTooltipField(
        verbose_name=_("Specifieke bewijs"),
    )
    localizedproduct_bezwaar_en_beroep = LabeledTooltipField(
        verbose_name=_("Specifieke bezwaar en beroep"),
    )
    localizedproduct_kosten_en_betaalmethoden = LabeledTooltipField(
        verbose_name=_("Specifieke kosten en betaalmethoden"),
    )
    localizedproduct_uiterste_termijn = LabeledTooltipField(
        verbose_name=_("Specifieke uiterste termijn"),
    )
    localizedproduct_wtd_bij_geen_reactie = LabeledTooltipField(
        verbose_name=_("Specifieke wtd bij geen reactie"),
    )
    localizedproduct_decentrale_procedure_link = LabeledTooltipField(
        verbose_name=_("Specifieke decentrale procedure link"),
    )
    localizedproduct_product_valt_onder_toelichting = LabeledTooltipField(
        verbose_name=_("Specifieke product valt onder toelichting"),
    )

    def for_field(self, prefix, name):
        return getattr(self, "{}_{}".format(prefix, name), None)

    def __str__(self):
        return "Product field configuratie"

    class Meta:
        verbose_name = _("Product field configuratie")
        verbose_name_plural = _("Product field configuratie")

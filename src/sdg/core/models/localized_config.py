from django.db import models
from django.utils.translation import gettext_lazy as _

from sdg.core.models import LabeledTooltipField
from sdg.producten.models.mixins import TaalMixin


class LocalizedProductFieldConfiguration(TaalMixin, models.Model):
    """
    Configuration for the CMS product fields.
    Field format: [lowercase model]_[field]
    """

    config = models.ForeignKey(
        "core.ProductFieldConfiguration",
        on_delete=models.PROTECT,
        verbose_name=_("configuratie"),
        help_text=_("De configuratie singelton van deze vertaling."),
    )

    localizedproduct_product_aanwezig_toelichting = LabeledTooltipField(
        verbose_name=_("Product aanwezig toelichting"),
    )
    localizedproduct_product_valt_onder_toelichting = LabeledTooltipField(
        verbose_name=_("Product valt onder toelichting"),
    )

    localizedgeneriekproduct_product_titel = LabeledTooltipField(
        verbose_name=_("Product titel"),
    )
    localizedgeneriekproduct_generieke_tekst = LabeledTooltipField(
        verbose_name=_("Generieke tekst"),
    )
    localizedgeneriekproduct_korte_omschrijving = LabeledTooltipField(
        verbose_name=_("Korte omschrijving"),
    )
    localizedgeneriekproduct_datum_check = LabeledTooltipField(
        verbose_name=_("Datum check"),
    )
    localizedgeneriekproduct_verwijzing_links = LabeledTooltipField(
        verbose_name=_("Verwijzing links"),
    )
    localizedgeneriekproduct_landelijke_link = LabeledTooltipField(
        verbose_name=_("Landelijke link"),
    )

    localizedproduct_product_titel_decentraal = LabeledTooltipField(
        verbose_name=_("Product titel decentraal"),
    )
    localizedproduct_specifieke_tekst = LabeledTooltipField(
        verbose_name=_("Specifieke tekst"),
    )
    localizedproduct_verwijzing_links = LabeledTooltipField(
        verbose_name=_("Verwijzing links"),
    )
    localizedproduct_decentrale_link = LabeledTooltipField(
        verbose_name=_("Decentrale link"),
    )
    localizedproduct_datum_wijziging = LabeledTooltipField(
        verbose_name=_("Datum wijziging"),
    )
    localizedproduct_procedure_beschrijving = LabeledTooltipField(
        verbose_name=_("Procedure beschrijving"),
    )
    localizedproduct_vereisten = LabeledTooltipField(
        verbose_name=_("Vereisten"),
    )
    localizedproduct_bewijs = LabeledTooltipField(
        verbose_name=_("Bewijs"),
    )
    localizedproduct_bezwaar_en_beroep = LabeledTooltipField(
        verbose_name=_("Bezwaar en beroep"),
    )
    localizedproduct_kosten_en_betaalmethoden = LabeledTooltipField(
        verbose_name=_("Kosten en betaalmethoden"),
    )
    localizedproduct_uiterste_termijn = LabeledTooltipField(
        verbose_name=_("Uiterste termijn"),
    )
    localizedproduct_wtd_bij_geen_reactie = LabeledTooltipField(
        verbose_name=_("Wtd bij geen reactie"),
    )
    localizedproduct_decentrale_procedure_link = LabeledTooltipField(
        verbose_name=_("Decentrale procedure link"),
    )

    def for_field(self, prefix, name):
        if name != "config":
            return getattr(self, "{}_{}".format(prefix, name), None)

    class Meta:
        verbose_name = _("Vertaalde configuratie")
        verbose_name_plural = _("Vertaalde configuraties")
        ordering = ["-taal"]
        constraints = [
            models.UniqueConstraint(
                fields=["config", "taal"],
                name="unique_language_per_condig",
            )
        ]

    def __str__(self):
        return self.taal

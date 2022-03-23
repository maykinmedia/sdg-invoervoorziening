from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from solo.admin import SingletonModelAdmin

from sdg.core.models import ProductFieldConfiguration


@admin.register(ProductFieldConfiguration)
class ProductFieldConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (
            _("Algemene gegevens"),
            {
                "fields": [
                    "product_product_aanwezig",
                    "product_product_aanwezig_toelichting",
                    "product_locaties",
                    "productversie_publicatie_datum",
                    "product_product_valt_onder",
                ],
            },
        ),
        (
            _("Generieke gegevens"),
            {
                "fields": [
                    "localizedgeneriekproduct_product_titel",
                    "localizedgeneriekproduct_generieke_tekst",
                    "localizedgeneriekproduct_korte_omschrijving",
                    "localizedgeneriekproduct_datum_check",
                    "localizedgeneriekproduct_verwijzing_links",
                    "localizedgeneriekproduct_landelijke_link",
                ],
            },
        ),
        (
            _("Specifieke gegevens"),
            {
                "fields": [
                    "localizedproduct_product_titel_decentraal",
                    "localizedproduct_specifieke_tekst",
                    "localizedproduct_verwijzing_links",
                    "localizedproduct_decentrale_link",
                    "localizedproduct_datum_wijziging",
                    "localizedproduct_procedure_beschrijving",
                    "localizedproduct_vereisten",
                    "localizedproduct_bewijs",
                    "localizedproduct_bezwaar_en_beroep",
                    "localizedproduct_kosten_en_betaalmethoden",
                    "localizedproduct_uiterste_termijn",
                    "localizedproduct_wtd_bij_geen_reactie",
                    "localizedproduct_decentrale_procedure_link",
                    "localizedproduct_product_valt_onder_toelichting",
                ],
            },
        ),
    ]

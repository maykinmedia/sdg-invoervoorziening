from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from sdg.core.models import ProductFieldConfiguration, SiteConfiguration
from sdg.core.models.localized_config import LocalizedProductFieldConfiguration


class LocalizedProductFieldConfigurationInline(admin.StackedInline):
    fieldsets = [
        (
            _("Algemene gegevens"),
            {
                "classes": ("collapse",),
                "fields": [
                    "localizedproduct_product_aanwezig_toelichting",
                    "localizedproduct_product_valt_onder_toelichting",
                ],
            },
        ),
        (
            _("Generieke gegevens"),
            {
                "classes": ("collapse",),
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
                "classes": ("collapse",),
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
                    "localizedproduct_decentrale_procedure_label",
                ],
            },
        ),
    ]

    model = LocalizedProductFieldConfiguration
    extra = 0
    max_num = 0

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProductFieldConfiguration)
class ProductFieldConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (
            _("Algemene gegevens"),
            {
                "classes": ("collapse",),
                "fields": [
                    "product_product_aanwezig",
                    "product_bevoegde_organisatie",
                    "product_locaties",
                    "productversie_publicatie_datum",
                    "product_product_valt_onder",
                    "product_heeft_kosten",
                    "product_api_zichtbaarheid",
                ],
            },
        )
    ]

    inlines = (LocalizedProductFieldConfigurationInline,)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (
            _("Documentatie configuratie"),
            {
                "fields": [
                    "documentatie_titel",
                    "documentatie_link",
                ],
            },
        ),
        (
            _("Analytics configuratie"),
            {
                "classes": ("collapse",),
                "fields": [
                    "goatcounter_domain",
                ],
            },
        ),
    ]

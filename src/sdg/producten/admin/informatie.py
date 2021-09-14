from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import GeneriekProduct, ReferentieProduct, SpecifiekProduct


@admin.register(GeneriekProduct)
class ProductGeneriekInformatieAdmin(MarkdownxModelAdmin):
    model = GeneriekProduct

    list_display = (
        "get_upn_uri",
        "product_titel",
    )
    list_filter = ("datum_check",)
    ordering = ("datum_check", "product_titel")
    search_fields = (
        "product_titel",
        "upn__uri",
        "upn__label",
    )

    def get_upn_uri(self, obj):
        return obj.upn.upn_uri


@admin.register(ReferentieProduct)
class ReferentieProductInformatieAdmin(MarkdownxModelAdmin):
    model = ReferentieProduct


@admin.register(SpecifiekProduct)
class ProductSpecifiekInformatieAdmin(MarkdownxModelAdmin):
    model = SpecifiekProduct

    list_display = ("upn_uri", "product_titel_decentraal", "versie")
    list_filter = ("publicatie_datum",)
    ordering = ("publicatie_datum", "product_titel_decentraal")
    search_fields = (
        "product_titel",
        "upn_uri",
    )

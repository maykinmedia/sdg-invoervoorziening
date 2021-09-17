from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    ProductGeneriekInformatie,
    ProductReferentieInformatie,
    ProductSpecifiekInformatie,
)


@admin.register(ProductGeneriekInformatie)
class ProductGeneriekInformatieAdmin(MarkdownxModelAdmin):
    model = ProductGeneriekInformatie

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


@admin.register(ProductReferentieInformatie)
class ProductReferentieInformatieAdmin(MarkdownxModelAdmin):
    model = ProductReferentieInformatie


@admin.register(ProductSpecifiekInformatie)
class ProductSpecifiekInformatieAdmin(MarkdownxModelAdmin):
    model = ProductSpecifiekInformatie

    list_display = ("product_titel_decentraal",)
    list_filter = ("datum_wijziging",)
    ordering = ("datum_wijziging", "product_titel_decentraal")
    search_fields = (
        "product_titel",
        "upn_uri",
    )

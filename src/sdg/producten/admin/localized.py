from django.contrib import admin

from sdg.producten.models import LocalizedGeneriekProduct, LocalizedProduct


@admin.register(LocalizedGeneriekProduct)
class LocalizedGeneriekProductAdmin(admin.ModelAdmin):
    model = LocalizedGeneriekProduct

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


@admin.register(LocalizedProduct)
class LocalizedProductAdmin(admin.ModelAdmin):
    model = LocalizedProduct

    list_display = ("product_titel_decentraal",)
    list_filter = ("datum_wijziging",)
    ordering = ("datum_wijziging", "product_titel_decentraal")
    search_fields = (
        "product_titel",
        "upn_uri",
    )

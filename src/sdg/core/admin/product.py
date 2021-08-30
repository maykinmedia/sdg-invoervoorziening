from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from sdg.core.models import (
    ProductGeneriekInformatie,
    ProductSpecifiekAanvraag,
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


class SpecifiekAanvraagInline(admin.StackedInline):
    model = ProductSpecifiekAanvraag
    can_delete = False
    extra = 1
    max_num = 1


@admin.register(ProductSpecifiekInformatie)
class ProductSpecifiekInformatieAdmin(MarkdownxModelAdmin):
    model = ProductSpecifiekInformatie

    list_display = ("upn_uri", "product_titel_decentraal", "versie")
    list_filter = ("publicatie_datum",)
    ordering = ("publicatie_datum", "product_titel_decentraal")
    search_fields = (
        "product_titel",
        "upn_uri",
    )
    inlines = (SpecifiekAanvraagInline,)


@admin.register(ProductSpecifiekAanvraag)
class ProductSpecifiekAnvraagAdmin(MarkdownxModelAdmin):
    model = ProductSpecifiekAanvraag

    list_display = (
        "get_product_title",
        "decentrale_procedure_link",
        "beschikbare_talen",
    )
    search_fields = (
        "upn_label",
        "upn_uri",
    )

    def get_product_title(self, obj):
        return obj.specifiek_product.product_title_decentraal

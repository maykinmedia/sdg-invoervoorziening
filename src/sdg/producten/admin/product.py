from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
)


class LocalizedGeneriekProductInline(admin.StackedInline):
    model = LocalizedGeneriekProduct
    extra = 1


class LocalizedProductInline(admin.StackedInline):
    model = LocalizedProduct
    extra = 1


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(MarkdownxModelAdmin):
    list_display = ("upn_label", "verplicht_product")
    list_filter = (
        "verantwoordelijke_organisatie",
        "verplicht_product",
    )
    inlines = (LocalizedGeneriekProductInline,)


@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):
    list_display = (
        "upn_label",
        "lokale_overheid",
        "catalogus",
        "referentie_product",
        "generiek_product",
    )
    list_filter = (
        "catalogus__lokale_overheid",
        "generiek_product",
    )
    inlines = (LocalizedProductInline,)

    def lokale_overheid(self, obj):
        return obj.catalogus.lokale_overheid

    lokale_overheid.admin_order_field = "catalogus__lokale_overheid"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Ervoor zorgen dat alleen referentieproducten kunnen worden geselecteerd.
        """

        if db_field.name == "referentie_product":
            kwargs["queryset"] = Product.objects.filter(referentie_product=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

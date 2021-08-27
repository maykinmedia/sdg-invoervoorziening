from django.contrib import admin

from sdg.core.models import ProductenCatalogus, ProductSpecifiekInformatie


@admin.register(ProductenCatalogus)
class CatalogusAdmin(admin.ModelAdmin):
    model = ProductenCatalogus

    list_display = ("naam", "domein", "versie")
    list_filter = ("domein", "naam")
    ordering = ("domein", "naam")
    search_fields = (
        "naam",
        "domein",
    )

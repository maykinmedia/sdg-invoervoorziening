from django.contrib import admin

from sdg.core.models import ProductenCatalogus


@admin.register(ProductenCatalogus)
class CatalogusAdmin(admin.ModelAdmin):
    model = ProductenCatalogus

    list_display = (
        "naam",
        "domein",
        "lokale_overheid",
        "referentie_catalogus",
        "is_referentie_catalogus",
        "versie",
    )
    list_filter = ("is_referentie_catalogus", "domein", "naam")
    ordering = ("domein", "naam")
    search_fields = (
        "naam",
        "domein",
    )
    autocomplete_fields = (
        "referentie_catalogus",
        "lokale_overheid",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Ensure that only reference catalogs can be selected.
        """

        if db_field.name == "referentie_catalogus":
            kwargs["queryset"] = ProductenCatalogus.objects.filter(
                is_referentie_catalogus=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

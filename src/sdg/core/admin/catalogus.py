from django.contrib import admin

from sdg.core.models import ProductenCatalogus


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Zorg ervoor dat alleen referentiecatalogi kunnen worden geselecteerd.
        """

        if db_field.name == "referentie_catalogus":
            kwargs["queryset"] = ProductenCatalogus.objects.filter(
                is_referentie_catalogus=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

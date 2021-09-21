from django.contrib import admin

from sdg.core.models import ProductenCatalogus


class IsReferenceCatalogFilter(admin.SimpleListFilter):
    title = "Is Referentie"
    parameter_name = "is_referentie_catalogus"

    def lookups(self, request, model_admin):
        return (
            ("Ja", "Ja"),
            ("Nee", "Nee"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Ja":
            return queryset.filter(is_referentie_catalogus=True)
        elif value == "Nee":
            return queryset.filter(is_referentie_catalogus=False)
        return queryset


@admin.register(ProductenCatalogus)
class CatalogusAdmin(admin.ModelAdmin):
    model = ProductenCatalogus

    list_display = ("naam", "domein", "versie")
    list_filter = ("domein", "naam", IsReferenceCatalogFilter)
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

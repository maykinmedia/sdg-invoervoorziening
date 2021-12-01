from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "referentie_catalogus",
                "lokale_overheid",
                "lokale_overheid__organisatie",
            )
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

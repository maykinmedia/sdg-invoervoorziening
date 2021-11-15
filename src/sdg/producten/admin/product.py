from django.contrib import admin

from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)


class IsReferenceProductFilter(admin.SimpleListFilter):
    title = "Is Referentie"
    parameter_name = "referentie_product"

    def lookups(self, request, model_admin):
        return (
            ("Ja", "Ja"),
            ("Nee", "Nee"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Ja":
            return queryset.filter(referentie_product__isnull=True)
        elif value == "Nee":
            return queryset.filter(referentie_product__isnull=False)
        return queryset


class LocalizedGeneriekProductInline(admin.StackedInline):
    model = LocalizedGeneriekProduct
    extra = 0


class LocalizedProductInline(admin.StackedInline):
    model = LocalizedProduct
    extra = 0


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(admin.ModelAdmin):
    list_display = ("upn_label", "verplicht_product")
    list_filter = (
        "verantwoordelijke_organisatie",
        "verplicht_product",
    )
    inlines = (LocalizedGeneriekProductInline,)
    autocomplete_fields = ("verantwoordelijke_organisatie", "upn")
    search_fields = ("upn_label",)


class ProductVersieInlineAdmin(admin.StackedInline):
    list_display = (
        "gemaakt_door",
        "versie",
        "publicatie_datum",
        "gemaakt_op",
        "gewijzigd_op",
    )
    model = ProductVersie
    extra = 1


@admin.register(ProductVersie)
class ProductVersieAdmin(admin.ModelAdmin):
    list_display = (
        "versie",
        "product",
        "lokale_overheid",
        "gemaakt_door",
        "publicatie_datum",
        "gemaakt_op",
        "gewijzigd_op",
    )
    inlines = (LocalizedProductInline,)
    ordering = ("-publicatie_datum",)

    def lokale_overheid(self, obj):
        return obj.product.catalogus.lokale_overheid

    lokale_overheid.admin_order_field = "product__catalogus__lokale_overheid"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "upn_label",
        "is_referentie",
        "lokale_overheid",
        "catalogus",
        "referentie_product",
        "generiek_product",
    )
    list_filter = (
        "catalogus__lokale_overheid",
        "generiek_product",
        IsReferenceProductFilter,
    )
    inlines = (ProductVersieInlineAdmin,)
    autocomplete_fields = (
        "generiek_product",
        "referentie_product",
        "catalogus",
    )
    search_fields = ("upn_label",)

    def is_referentie(self, obj):
        return obj.is_referentie_product

    is_referentie.boolean = True

    def lokale_overheid(self, obj):
        return obj.catalogus.lokale_overheid

    lokale_overheid.admin_order_field = "catalogus__lokale_overheid"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ensure that only reference products can be selected."""

        if db_field.name == "referentie_product":
            kwargs["queryset"] = Product.objects.filter(referentie_product=None)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Ensure that only locations belonging to a product's municipality can be selected."""

        object_id = request.resolver_match.kwargs.get("object_id", None)
        if db_field.name == "lokaties" and object_id:
            kwargs["queryset"] = Product.objects.get(
                pk=object_id
            ).get_municipality_locations()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

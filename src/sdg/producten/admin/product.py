from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from sdg.core.admin.mixins import BaseProductFilter
from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)


class IsReferenceProductFilter(BaseProductFilter):
    title = _("Is Referentie")
    parameter_name = "referentie_product"
    filter_field = "referentie_product__isnull"


class LocalizedGeneriekProductInline(admin.StackedInline):
    model = LocalizedGeneriekProduct
    extra = 0


class LocalizedProductInline(admin.StackedInline):
    model = LocalizedProduct
    extra = 0


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(admin.ModelAdmin):
    list_display = (
        "upn_label",
        "doelgroep",
        "verplicht_product",
        "verantwoordelijke_organisatie",
    )
    list_filter = (
        "doelgroep",
        "verplicht_product",
    )
    inlines = (LocalizedGeneriekProductInline,)
    autocomplete_fields = ("verantwoordelijke_organisatie", "upn")
    search_fields = ("upn__upn_label",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("upn")


class ProductVersieInlineAdmin(admin.StackedInline):
    list_display = (
        "gemaakt_door",
        "versie",
        "publicatie_datum",
        "gemaakt_op",
        "gewijzigd_op",
    )
    autocomplete_fields = ("gemaakt_door",)
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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "product__generiek_product",
                "product__generiek_product__upn",
                "product__referentie_product",
                "product__referentie_product__generiek_product",
                "product__referentie_product__generiek_product__upn",
                "product__catalogus",
                "product__catalogus__lokale_overheid",
                "product__catalogus__lokale_overheid__organisatie",
            )
        )

    def lokale_overheid(self, obj):
        return obj.product.catalogus.lokale_overheid

    lokale_overheid.admin_order_field = "product__catalogus__lokale_overheid"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_referentie",
        "lokale_overheid",
        "catalogus",
        "generic_product",
    )
    list_filter = (
        IsReferenceProductFilter,
        "catalogus__lokale_overheid",
    )
    inlines = (ProductVersieInlineAdmin,)
    autocomplete_fields = (
        "generiek_product",
        "referentie_product",
        "catalogus",
        "gerelateerde_producten",
        "bevoegde_organisatie",
        "locaties",
        "product_valt_onder",
    )
    search_fields = (
        "generiek_product__upn__upn_label",
        "referentie_product__generiek_product__upn__upn_label",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .annotate_name()
            .select_related(
                "generiek_product",
                "generiek_product__upn",
                "referentie_product",
                "referentie_product__generiek_product",
                "referentie_product__generiek_product__upn",
                "catalogus",
                "catalogus__lokale_overheid",
                "catalogus__lokale_overheid__organisatie",
            )
        )

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
        if db_field.name == "locaties" and object_id:
            kwargs["queryset"] = Product.objects.get(
                pk=object_id
            ).get_municipality_locations()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

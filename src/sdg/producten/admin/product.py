from django import forms
from django.contrib import admin
from django.db.models import Count, F
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
        "eind_datum",
        "product_status",
    )
    list_filter = (
        "doelgroep",
        "verplicht_product",
    )
    inlines = (LocalizedGeneriekProductInline,)
    readonly_fields = ("product_status",)
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


class ProductVersieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product_versie = kwargs["instance"]
        self.fields["product"].queryset = Product.objects.filter(
            catalogus__lokale_overheid=product_versie.product.catalogus.lokale_overheid
        )


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
    form = ProductVersieForm

    inlines = (LocalizedProductInline,)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "product__generiek_product",
                "product__generiek_product__upn",
                "product__referentie_product",
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
        "product_aanwezig",
        "latest_version",
        "latest_publication_date",
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
    search_fields = ("generiek_product__upn__upn_label",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .annotate_name()
            .select_related(
                "generiek_product",
                "generiek_product__upn",
                "referentie_product",
                "catalogus",
                "catalogus__lokale_overheid",
                "catalogus__lokale_overheid__organisatie",
            )
            .annotate(versie_nummer=Count("versies", distinct=True))
        )

    def is_referentie(self, obj):
        return obj.is_referentie_product

    is_referentie.boolean = True

    def latest_version(self, obj):
        return obj.versie_nummer

    def latest_publication_date(self, obj):
        return ProductVersie.objects.get(
            product=obj, versie=obj.versie_nummer
        ).publicatie_datum

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

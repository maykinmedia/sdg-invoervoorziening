from django import forms
from django.contrib import admin
from django.db.models import Max
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from sdg.core.admin.mixins import BaseProductFilter

from ..models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)
from .filters import IsSDGProductFilter


class IsReferenceProductFilter(BaseProductFilter):
    title = _("is referentie")
    parameter_name = "referentie_product"
    filter_field = "referentie_product__isnull"


class OrganisationTypeFilter(admin.SimpleListFilter):
    title = _("organisatie type")
    parameter_name = "organisation_type"

    def lookups(self, request, model_admin):
        return (
            ("municipality", _("Gemeente")),
            ("province", _("Provincie")),
            ("waterauthority", _("Waterschap")),
        )

    def queryset(self, request, queryset):
        if self.value() in dict(self.lookup_choices).keys():
            if self.value() == "municipality":
                return queryset.filter(upn__gemeente=1)
            elif self.value() == "province":
                return queryset.filter(upn__provincie=1)
            elif self.value() == "waterauthority":
                return queryset.filter(upn__waterschap=1)
        return queryset


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
        "eind_datum",
        "product_status",
        "is_sdg_product",
    )
    list_filter = (
        IsSDGProductFilter,
        OrganisationTypeFilter,
        "doelgroep",
        "product_status",
        "verplicht_product",
    )
    inlines = (LocalizedGeneriekProductInline,)
    readonly_fields = ("product_status", "is_sdg_product")
    autocomplete_fields = ("verantwoordelijke_organisatie", "upn")
    search_fields = ("upn__upn_label",)

    # Turns boolean into icon
    def is_sdg_product(self, obj):
        return obj.is_sdg_product

    is_sdg_product.boolean = True

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
        product_versie = kwargs.get("instance")
        if product_versie:
            self.fields["product"].queryset = Product.objects.filter(
                catalogus__lokale_overheid=product_versie.product.catalogus.lokale_overheid
            )


@admin.register(ProductVersie)
class ProductVersieAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "doelgroep",
        "catalogus",
        "versie",
        "gemaakt_door",
        "publicatie_datum",
        "gemaakt_op",
        "gewijzigd_op",
    )
    list_filter = (
        "product__generiek_product__doelgroep",
        "product__catalogus",
        "product__generiek_product__upn",
    )
    search_fields = ("product__generiek_product__upn__upn_label",)

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

    def doelgroep(self, obj):
        return obj.product.generiek_product.doelgroep

    doelgroep.admin_order_field = "product__generiek_product__doelgroep"

    def catalogus(self, obj):
        return obj.product.catalogus

    catalogus.admin_order_field = "product__catalogus__lokale_overheid"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "doelgroep",
        "catalogus",
        "latest_version",
        "is_referentie",
        "product_aanwezig",
        "latest_publication_date",
        "api_verborgen",
    )
    list_filter = (
        IsReferenceProductFilter,
        "generiek_product__doelgroep",
        "catalogus",
        "generiek_product__upn",
    )
    inlines = (ProductVersieInlineAdmin,)
    autocomplete_fields = (
        "generiek_product",
        "referentie_product",
        "catalogus",
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
            .annotate(versie_nummer=Max("versies__versie"))
            .annotate(publication_date=Max("versies__publicatie_datum"))
        )

    def is_referentie(self, obj):
        return obj.is_referentie_product

    is_referentie.boolean = True

    def latest_version(self, obj):
        return obj.versie_nummer

    def latest_publication_date(self, obj):
        return obj.publication_date

    def doelgroep(self, obj):
        return obj.generiek_product.doelgroep

    doelgroep.admin_order_field = "generiek_product__doelgroep"

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

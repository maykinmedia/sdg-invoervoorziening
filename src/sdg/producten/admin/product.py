from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    GeneriekProduct,
    Product,
    ProductGeneriekInformatie,
    ProductInformatie,
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


class ProductGeneriekInformatieInline(admin.StackedInline):
    model = ProductGeneriekInformatie
    extra = 1


class ProductInformatieInline(admin.StackedInline):
    model = ProductInformatie
    extra = 1


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(MarkdownxModelAdmin):
    model = GeneriekProduct
    inlines = (ProductGeneriekInformatieInline,)


@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):
    model = Product
    inlines = (ProductInformatieInline,)
    list_filter = (IsReferenceProductFilter,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Ervoor zorgen dat alleen referentieproducten kunnen worden geselecteerd.
        """

        if db_field.name == "referentie_product":
            kwargs["queryset"] = Product.objects.filter(referentie_product=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

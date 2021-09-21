from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    GeneriekProduct,
    ProductGeneriekInformatie,
    ProductSpecifiekInformatie,
    SpecifiekProduct,
)


class ProductGeneriekInformatieInline(admin.StackedInline):
    model = ProductGeneriekInformatie
    extra = 1


class ProductSpecifiekInformatieInline(admin.StackedInline):
    model = ProductSpecifiekInformatie
    extra = 1


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(MarkdownxModelAdmin):
    model = GeneriekProduct
    inlines = (ProductGeneriekInformatieInline,)


@admin.register(SpecifiekProduct)
class SpecifiekProductAdmin(MarkdownxModelAdmin):
    model = SpecifiekProduct
    inlines = (ProductSpecifiekInformatieInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Ervoor zorgen dat alleen referentieproducten kunnen worden geselecteerd.
        """

        if db_field.name == "referentie_product":
            kwargs["queryset"] = SpecifiekProduct.objects.filter(
                referentie_product=None
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    GeneriekProduct,
    ProductGeneriekInformatie,
    ProductReferentieInformatie,
    ProductSpecifiekInformatie,
    ReferentieProduct,
    SpecifiekProduct,
)


class ProductGeneriekInformatieInline(admin.StackedInline):
    model = ProductGeneriekInformatie
    extra = 1


class ProductReferentieInformatieInline(admin.StackedInline):
    model = ProductReferentieInformatie
    extra = 1


class ProductSpecifiekInformatieInline(admin.StackedInline):
    model = ProductSpecifiekInformatie
    extra = 1


@admin.register(GeneriekProduct)
class GeneriekProductAdmin(MarkdownxModelAdmin):
    model = GeneriekProduct
    inlines = (ProductGeneriekInformatieInline,)


@admin.register(ReferentieProduct)
class ReferentieProductAdmin(MarkdownxModelAdmin):
    model = ReferentieProduct
    inlines = (ProductReferentieInformatieInline,)


@admin.register(SpecifiekProduct)
class SpecifiekProductAdmin(MarkdownxModelAdmin):
    model = SpecifiekProduct
    inlines = (ProductSpecifiekInformatieInline,)

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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    GeneriekProduct,
    Product,
    ProductGeneriekInformatie,
    ProductInformatie,
)


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

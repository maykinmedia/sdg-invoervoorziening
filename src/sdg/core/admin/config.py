from django.contrib import admin

from sdg.core.models import ProductFieldConfiguration


@admin.register(
    ProductFieldConfiguration,
)
class ProductFieldConfigurationAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin

from sdg.services.models import ServiceConfiguration


@admin.register(ServiceConfiguration)
class ServiceConfigurationAdmin(admin.ModelAdmin):
    pass

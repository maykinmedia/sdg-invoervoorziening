from django.contrib import admin

from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)


@admin.register(Overheidsorganisatie)
class OverheidsorganisatieAdmin(admin.ModelAdmin):
    search_fields = ("owms_pref_label",)
    list_display = ("owms_pref_label", "owms_identifier", "owms_end_date")


@admin.register(Informatiegebied)
class InformatiegebiedAdmin(admin.ModelAdmin):
    search_fields = ("code", "informatiegebied")
    list_display = ("code", "informatiegebied")


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    search_fields = ("thema",)
    list_display = ("thema", "informatiegebied")


@admin.register(UniformeProductnaam)
class UniformeProductnaamAdmin(admin.ModelAdmin):
    search_fields = ("upn_label",)
    list_display = ("upn_label", "thema")
    autocomplete_fields = ("thema",)

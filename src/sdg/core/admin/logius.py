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


@admin.register(Informatiegebied)
class InformatiegebiedAdmin(admin.ModelAdmin):
    search_fields = ("code", "informatiegebied")


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    search_fields = ("thema",)


@admin.register(UniformeProductnaam)
class UniformeProductnaamAdmin(admin.ModelAdmin):
    search_fields = ("upn_label",)

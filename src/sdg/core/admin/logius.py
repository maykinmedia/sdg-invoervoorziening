from django.contrib import admin

from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)


@admin.register(Overheidsorganisatie)
class OverheidsorganisatieAdmin(admin.ModelAdmin):
    model = Overheidsorganisatie


@admin.register(Informatiegebied)
class InformatiegebiedAdmin(admin.ModelAdmin):
    model = Informatiegebied


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    model = Thema


@admin.register(UniformeProductnaam)
class UniformeProductnaamAdmin(admin.ModelAdmin):
    model = UniformeProductnaam

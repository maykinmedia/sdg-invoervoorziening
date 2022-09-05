from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

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
    search_fields = ("informatiegebied",)
    list_display = ("informatiegebied",)


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    search_fields = ("thema",)
    list_display = ("code", "thema", "informatiegebied")


@admin.register(UniformeProductnaam)
class UniformeProductnaamAdmin(admin.ModelAdmin):
    search_fields = ("upn_label",)
    list_display = ("upn_label", "thema", "is_verwijderd")
    list_filter = (
        "is_verwijderd",
        "sdg",
        "gemeente",
        "rijk",
        "provincie",
        "waterschap",
        "burger",
        "bedrijf",
    )
    autocomplete_fields = ("thema",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "thema",
            )
        )

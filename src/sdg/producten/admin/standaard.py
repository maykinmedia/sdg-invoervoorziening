from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from markdownx.admin import MarkdownxModelAdmin

from sdg.producten.models import (
    StandaardProductSpecifiekAanvraag,
    StandaardProductSpecifiekInformatie,
    StandaardProductuitvoering,
)


@admin.register(StandaardProductSpecifiekInformatie)
class StandaardProductSpecifiekInformatieAdmin(MarkdownxModelAdmin):
    model = StandaardProductSpecifiekInformatie

    list_display = ("product_titel_decentraal", "decentrale_link", "datum_wijziging")
    ordering = ("datum_wijziging", "product_titel_decentraal")
    search_fields = ("product_titel_decentraal",)


@admin.register(StandaardProductSpecifiekAanvraag)
class StandardProductAanvraagAdmin(MarkdownxModelAdmin):
    model = StandaardProductSpecifiekAanvraag


@admin.register(StandaardProductuitvoering)
class StandaardProductuitvoeringAdmin(MarkdownxModelAdmin):
    model = StandaardProductuitvoering

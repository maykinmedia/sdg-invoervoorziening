from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from sdg.core.models import (
    StandaardProductSpecifiekAanvraag,
    StandaardProductSpecifiekInformatie,
    StandaardProductuitvoering,
)


@admin.register(StandaardProductSpecifiekInformatie)
class StandaardProductSpecifiekInformatieAdmin(MarkdownxModelAdmin):
    model = StandaardProductSpecifiekInformatie


@admin.register(StandaardProductSpecifiekAanvraag)
class StandardProductAanvraagAdmin(MarkdownxModelAdmin):
    model = StandaardProductSpecifiekAanvraag


@admin.register(StandaardProductuitvoering)
class StandaardProductuitvoeringAdmin(MarkdownxModelAdmin):
    model = StandaardProductuitvoering

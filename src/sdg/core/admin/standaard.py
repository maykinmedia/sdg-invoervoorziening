from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from sdg.core.models import (
    StandaardProductSpecifiekAanvraag,
    StandaardProductSpecifiekInformatie,
    StandaardProductuitvoering,
)


class StandaardAdmin(MarkdownxModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(StandaardProductSpecifiekInformatie)
class StandaardProductSpecifiekInformatieAdmin(StandaardAdmin):
    model = StandaardProductSpecifiekInformatie


@admin.register(StandaardProductSpecifiekAanvraag)
class StandardProductAanvraagAdmin(StandaardAdmin):
    model = StandaardProductSpecifiekAanvraag


@admin.register(StandaardProductuitvoering)
class StandaardProductuitvoeringAdmin(StandaardAdmin):
    model = StandaardProductuitvoering

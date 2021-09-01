from django.contrib import admin

from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokatieInline(admin.StackedInline):
    model = Lokatie
    extra = 1


@admin.register(LokaleOverheid)
class LokaleOverheidAdmin(admin.ModelAdmin):
    model = LokaleOverheid

    list_display = ("organisatie", "contact_website", "contact_naam")
    ordering = ("organisatie__owms_pref_label",)
    search_fields = (
        "organisatie__owms_pref_label",
        "contact_naam",
        "contact_emailadres",
        "contact_website",
    )
    inlines = (LokatieInline,)


@admin.register(Lokatie)
class LokatieAdmin(admin.ModelAdmin):
    model = Lokatie

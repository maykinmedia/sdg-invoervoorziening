from django.contrib import admin

from sdg.api.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "created")
    readonly_fields = ("key",)
    ordering = ("-created",)

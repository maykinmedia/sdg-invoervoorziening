from django.conf import settings
from django.contrib import admin

from sdg.api.models import Token, TokenAuthorization


class TokenAuthorizationInline(admin.TabularInline):
    model = TokenAuthorization
    extra = 1
    autocomplete_fields = ("lokale_overheid",)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("organization", "contact_person", "created", "whitelisted_ips")
    readonly_fields = ("key", "last_seen")
    ordering = ("organization",)
    inlines = (TokenAuthorizationInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if settings.SDG_API_WHITELISTING_ENABLED:
            form.base_fields["whitelisted_ips"].required = True
        return form

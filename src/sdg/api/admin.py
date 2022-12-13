from django.conf import settings
from django.contrib import admin

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from sdg.api.models import Token, TokenAuthorization


class TokenAuthorizationInline(admin.TabularInline):
    model = TokenAuthorization
    extra = 1
    autocomplete_fields = ("lokale_overheid",)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = (
        "contact_person",
        "organization",
        "last_seen",
        "created",
        "whitelisted_ips",
        "api_default_most_recent",
    )

    readonly_fields = ("key", "last_seen")
    ordering = ("organization",)
    inlines = (TokenAuthorizationInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if settings.SDG_API_WHITELISTING_ENABLED:
            form.base_fields["whitelisted_ips"].required = True
        return form

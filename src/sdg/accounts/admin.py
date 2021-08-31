from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import ugettext_lazy as _

from hijack_admin.admin import HijackUserAdminMixin

from .models import Role

User = get_user_model()


@admin.register(User)
class UserAdmin(_UserAdmin, HijackUserAdminMixin):
    fieldsets = _UserAdmin.fieldsets + (
        (_("Roles"), {"fields": ("is_hoofdredacteur",)}),
    )
    search_fields = ["first_name"]
    list_display = _UserAdmin.list_display + (
        "is_hoofdredacteur",
        "hijack_field",
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    model = Role

    list_display = (
        "get_role_user",
        "get_role_organization",
        "is_beheerder",
        "is_redacteur",
    )
    list_filter = (
        "user__username",
        "lokale_overheid__organisatie__owms_pref_label",
        "is_beheerder",
        "is_redacteur",
    )

    def get_role_user(self, obj):
        return obj.user.username

    get_role_user.short_description = _("User")

    def get_role_organization(self, obj):
        return obj.lokale_overheid.organisatie.owms_pref_label

    get_role_organization.short_description = _("Organization")

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import ugettext_lazy as _

from hijack_admin.admin import HijackUserAdminMixin

from .models import Role

User = get_user_model()


class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

    def get_role_user(self, obj):
        return obj.user.email

    get_role_user.short_description = _("Gebruik")

    def get_role_organization(self, obj):
        return obj.lokale_overheid.organisatie.owms_pref_label

    get_role_organization.short_description = _("Organisatie")


@admin.register(User)
class UserAdmin(_UserAdmin, HijackUserAdminMixin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "hijack_field",
    )
    ordering = ("email",)
    inlines = (RoleInline,)

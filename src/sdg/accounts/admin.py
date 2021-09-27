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
        return obj.user.username

    get_role_user.short_description = _("Gebruik")

    def get_role_organization(self, obj):
        return obj.lokale_overheid.organisatie.owms_pref_label

    get_role_organization.short_description = _("Organisatie")


@admin.register(User)
class UserAdmin(_UserAdmin, HijackUserAdminMixin):
    search_fields = ["first_name"]
    list_display = _UserAdmin.list_display + ("hijack_field",)
    inlines = (RoleInline,)

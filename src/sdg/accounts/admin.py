from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _

from hijack_admin.admin import HijackUserAdminMixin

from ..core.events import post_event
from .models import Role

User = get_user_model()


class RoleInline(admin.TabularInline):
    model = Role
    extra = 1
    autocomplete_fields = ("lokale_overheid",)

    def get_role_user(self, obj):
        return obj.user.email

    get_role_user.short_description = _("Gebruiker")

    def get_role_organization(self, obj):
        return obj.lokale_overheid.organisatie.owms_pref_label

    get_role_organization.short_description = _("Organisatie")


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user (with an unusable password) from the given email and name.
    """

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
                {"autofocus": True}
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(_UserAdmin, HijackUserAdminMixin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Persoonlijke informatie"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Rechten"),
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
        (_("Overige"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name"),
            },
        ),
    )
    add_form = UserCreationForm
    search_fields = ("email", "first_name", "last_name")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "organisaties",
        "is_staff",
        "hijack_field",
    )
    ordering = ("email",)
    inlines = (RoleInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("roles__lokale_overheid__organisatie")
        )

    def organisaties(self, obj):
        return ", ".join(
            [str(role.lokale_overheid.organisatie) for role in obj.roles.all()]
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:  # new user
            errors = post_event("save_user", user=form.instance, request=request)

            if not errors:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _("Een uitnodiging is succesvol naar de gebruiker verzonden."),
                )
                return

            for function, exception in errors.items():
                messages.add_message(
                    request, messages.ERROR, f"{function}: {exception}"
                )

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from allauth.account.models import EmailAddress
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

from ..core.events import post_event
from .models import Role, UserInvitation

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


class UserInvitationInline(admin.TabularInline):
    model = UserInvitation
    fields = (
        "key",
        "accepted",
        "created",
        "sent",
        "inviter",
        "resend",
    )
    readonly_fields = ("resend",)
    fk_name = "user"
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    def resend(self, obj):
        subpath = settings.SUBPATH or ""
        disabled = "disabled" if obj.accepted else None

        return format_html(
            f"<input type='button' value='resend invite' onclick='resendInvite({obj.pk}, \"{subpath}\")' {disabled}>"
        )

    resend.allow_tags = True

    class Media:
        js = ("js/admin/resend_invite.js",)


class EmailaddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


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
class UserAdmin(_UserAdmin):
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
    )
    ordering = ("email",)
    inlines = (RoleInline, UserInvitationInline, EmailaddressInline)

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


# Add search and filter fields for the TOTP device admin page
TOTPDeviceAdmin.search_fields = ["user__first_name", "user__last_name"]
TOTPDeviceAdmin.list_filter = ["confirmed"]

from secrets import compare_digest

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
    UsernameField,
)
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from sdg.accounts.models import Role, User


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = (
            "is_beheerder",
            "is_redacteur",
        )


RoleInlineFormSet = inlineformset_factory(
    User, Role, form=RoleForm, extra=1, max_num=1, can_delete=False
)


class InvitationAcceptForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label=_("Wachtwoord"),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(), label=_("Wachtwoord bevestigen")
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data["password"]
        password_confirm = cleaned_data["password_confirm"]

        if not compare_digest(password, password_confirm):
            raise forms.ValidationError(
                _("Wachtwoord en bevestigingswachtwoord komen niet overeen")
            )


class AuthenticationForm(_AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={"autofocus": True}), required=False
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        required=False,
    )

    error_messages = {
        "invalid_login": "Voer een juist e-mailadres en wachtwoord in.",
        "inactive": _("This account is inactive."),
    }

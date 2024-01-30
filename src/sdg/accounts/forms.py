from secrets import compare_digest

from django import forms
from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import (
    PasswordField,
    PasswordVerificationMixin,
    SetPasswordField,
)

from sdg.accounts.models import Role, User


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ("is_beheerder", "is_redacteur", "is_raadpleger", "ontvangt_mail")


class RoleInlineFormSet(
    inlineformset_factory(
        User, Role, form=RoleForm, extra=1, max_num=1, can_delete=False
    )
):
    def clean(self):
        super().clean()

        for form in self.forms:
            is_beheerder = form.cleaned_data.get("is_beheerder", False)
            is_redacteur = form.cleaned_data.get("is_redacteur", False)
            is_raadpleger = form.cleaned_data.get("is_raadpleger", False)

            if sum([is_beheerder, is_redacteur, is_raadpleger]) == 0:
                raise forms.ValidationError(_("U moet ten minste één rol selecteren."))


class InvitationAcceptForm(PasswordVerificationMixin, forms.Form):
    password1 = SetPasswordField(label=_("Wachtwoord"))
    password2 = PasswordField(label=_("Wachtwoord bevestigen"))


class AuthenticationForm(_AuthenticationForm):
    """
    Override the default AuthenticationForm to use a custom error message.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["invalid_login"] = (
            "Voer een juist e-mailadres en wachtwoord in."
        )

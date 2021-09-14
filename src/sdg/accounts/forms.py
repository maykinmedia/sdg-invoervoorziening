from django.urls import reverse
from django.utils.translation import gettext as _

from allauth.account.forms import LoginForm, ResetPasswordForm, SignupForm

from sdg.core.forms.mixins import SdgFormMixin


class SdgLoginForm(SdgFormMixin, LoginForm):
    form_action = "account_login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._append_html(
            f"""
            <a class="secondaryAction" href="{reverse('account_reset_password')}">{_("Forgot Password?")}</a>
            """
        )
        self._insert_input_button("sign_in", _("Sign In"))


class SdgSignupForm(SdgFormMixin, SignupForm):
    form_action = "account_signup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insert_input_button("sign_up", _("Sign Up"))


class SdgResetPasswordForm(SdgFormMixin, ResetPasswordForm):
    form_action = "account_reset_password"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insert_input_button("reset_password", _("Reset password"))

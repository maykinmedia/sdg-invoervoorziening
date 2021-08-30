from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _

from allauth.account.forms import LoginForm, ResetPasswordForm, SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Div, Field, Fieldset, Layout, Submit


class SdgFormMixin(forms.Form):
    form_action = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.form_action = self.form_action

        self.helper.form_method = "POST"
        self.helper.form_class = "form"
        self.helper.label_class = "form__label"

        if getattr(self, "request", None):
            redirect_field_value = self.request.GET.get("next")
        else:
            redirect_field_value = None

        all_fields = [f for f in self.fields.keys()]
        self.helper.layout = Layout(
            Div(
                Div(
                    *[
                        Field(
                            f,
                            css_class="form__input",
                        )
                        for f in all_fields
                    ],
                    css_class="form__group",
                ),
                css_class="form__block",
            ),
        )
        if redirect_field_value:
            self.helper.layout[0].append(
                HTML(
                    """
                <input type="hidden" name="{{ redirect_field_name }}" value="{{ redirect_field_value }}"/>
                """
                )
            )

    def _insert_html(self, html):
        self.helper.layout[0][0].insert(HTML(html))

    def _append_html(self, html):
        self.helper.layout[0][0].append(HTML(html))

    def _insert_input_button(self, name, value):
        self.helper.add_input(
            Submit(
                name=name,
                value=value,
                css_class="primaryAction login_button button",
            )
        )


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

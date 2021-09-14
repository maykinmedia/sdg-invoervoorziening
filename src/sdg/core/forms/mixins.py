from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit


class SdgFormMixin(forms.Form):
    """
    Base SDG form, reusable for most basic forms.
    It will render all fields by default in the most basic way.
    """

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

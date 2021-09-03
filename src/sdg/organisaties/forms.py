from django import forms
from django.forms import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout

from sdg.core.forms.mixins import SdgFormMixin
from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokaleOverheidForm(SdgFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_tag = False

    class Meta:
        model = LokaleOverheid
        fields = (
            "ondersteunings_organisatie",
            "verantwoordelijke_organisatie",
            "bevoegde_organisatie",
            "organisatie",
            "lau_code",
            "contact_naam",
            "contact_website",
            "contact_telefoonnummer",
            "contact_emailadres",
        )


class LokatieFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = None
        self.layout = Layout(
            Div(
                Div(
                    Div(
                        Div(
                            Field("naam", css_class="form__input"),
                            Field("straat", css_class="form__input"),
                            Field("nummer", css_class="form__input"),
                            Field("plaats", css_class="form__input"),
                            Div(
                                Field("postcode", css_class="form__input"),
                                Field("land", css_class="form__input"),
                                css_class="form__table form__special-group",
                            ),
                            css_class="form__group",
                        ),
                    ),
                    Div(
                        HTML('<div class="form__table-header">Dag</div>'),
                        HTML('<div class="form__table-header">Openingstijden</div>'),
                        Field(
                            "maandag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "dinsdag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "woensdag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "donderdag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "vrijdag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "zaterdag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        Field(
                            "zondag",
                            css_class="form__input",
                            template="forms/simple_input.html",
                        ),
                        css_class="form__table",
                    ),
                    css_class="form__block-group",
                ),
                css_class="form__subform",
            ),
        )


class LokatieForm(forms.ModelForm):
    class Meta:
        model = Lokatie
        fields = (
            "naam",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        )


LokatieInlineFormSet = inlineformset_factory(
    LokaleOverheid, Lokatie, form=LokatieForm, extra=0
)

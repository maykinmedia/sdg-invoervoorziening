from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit

from sdg.producten.models import ProductReferentieInformatie


class ProductSpecifiekInformatieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.form_method = "POST"
        self.helper.form_class = "form"
        self.helper.label_class = "form__label"

        all_fields = [f for f in self.fields.keys()]
        self.helper.layout = Layout(
            *[
                Field(f, css_class="form__input", template="forms/table_field.html")
                for f in all_fields
            ],
        )

    class Meta:
        model = ProductReferentieInformatie
        fields = (
            "product_titel_decentraal",
            "specifieke_tekst",
            "verwijzing_links",
            "specifieke_link",
            "decentrale_link",
            "datum_wijziging",
        )

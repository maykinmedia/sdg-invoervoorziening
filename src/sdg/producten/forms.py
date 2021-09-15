from django import forms
from django.forms import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Hidden, Layout

from sdg.core.constants import TaalChoices
from sdg.producten.models import (
    ProductGegevensMixin,
    ProductReferentieInformatie,
    ReferentieProduct,
)


class GegevensFormHelper(FormHelper):
    form_field_names = (
        "product_titel_decentraal",
        "specifieke_tekst",
        "verwijzing_links",
        "specifieke_link",
        "decentrale_link",
        "datum_wijziging",
        "procedure_beschrijving",
        "vereisten",
        "bewijs",
        "bezwaar_en_beroep",
        "kosten_en_betaalmethoden",
        "uiterste_termijn",
        "wtd_bij_geen_reactie",
        "decentrale_procedure_link",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = None
        self.disable_csrf = True
        self.layout = Layout(
            Field("id", type="hidden"),
            Field("taal", type="hidden"),
            *[
                Field(f, css_class="form__input", template="forms/table_field.html")
                for f in self.form_field_names
            ],
        )


class ProductGegevensForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = GegevensFormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = "form"
        self.helper.label_class = "form__label"

    class Meta:
        model = ProductGegevensMixin
        fields = (
            "taal",
            "product_titel_decentraal",
            "specifieke_tekst",
            "verwijzing_links",
            "specifieke_link",
            "decentrale_link",
            "datum_wijziging",
            "procedure_beschrijving",
            "vereisten",
            "bewijs",
            "bezwaar_en_beroep",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "wtd_bij_geen_reactie",
            "decentrale_procedure_link",
        )


ProductReferentieInformatieFormset = inlineformset_factory(
    ReferentieProduct,
    ProductReferentieInformatie,
    form=ProductGegevensForm,
)

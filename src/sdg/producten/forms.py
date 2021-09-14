from django import forms
from django.forms import modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit

from sdg.producten.models import ProductGegevensMixin, ProductReferentieInformatie


class GegevensFormHelper(FormHelper):
    fields = (
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
        self.template = "forms/whole_uni_formset.html"
        self.layout = Layout(
            *[
                Field(f, css_class="form__input", template="forms/table_field.html")
                for f in self.fields
            ],
        )


class ProductGegevensForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.form_method = "POST"
        self.helper.form_class = "form"
        self.helper.label_class = "form__label"

    class Meta:
        model = ProductGegevensMixin
        fields = (
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


ProductReferentieInformatieFormset = modelformset_factory(
    ProductReferentieInformatie,
    form=ProductGegevensForm,
)

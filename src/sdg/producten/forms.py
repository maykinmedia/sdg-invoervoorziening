from django import forms
from django.utils.timezone import now

from sdg.producten.constants import PublishChoices
from sdg.producten.models import LocalizedProduct, ProductVersie


class LocalizedProductForm(forms.ModelForm):
    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "product_titel_decentraal",
            "specifieke_tekst",
            "verwijzing_links",
            "specifieke_link",
            "decentrale_link",
            "procedure_beschrijving",
            "vereisten",
            "bewijs",
            "bezwaar_en_beroep",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "wtd_bij_geen_reactie",
            "decentrale_procedure_link",
        )


class ProductVersionForm(forms.ModelForm):
    publish = forms.ChoiceField(choices=PublishChoices.choices)
    date = forms.DateTimeField(required=False)

    class Meta:
        model = ProductVersie
        fields = (
            "product",
            "gemaakt_door",
            "versie",
            "publicatie_datum",
        )

    def clean(self):
        cleaned_data = super().clean()

        now_ = now()
        if cleaned_data["publish"] == "now":
            cleaned_data["publicatie_datum"] = now_
        else:
            cleaned_data["publicatie_datum"] = cleaned_data.get("date", None)

        return cleaned_data

from django import forms

from .models import LocalizedProduct


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
            # "datum_wijziging",
            "procedure_beschrijving",
            "vereisten",
            "bewijs",
            "bezwaar_en_beroep",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "wtd_bij_geen_reactie",
            "decentrale_procedure_link",
        )

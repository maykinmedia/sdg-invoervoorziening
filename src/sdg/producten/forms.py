from datetime import date
from typing import Optional

from django import forms

from .constants import PublishChoices
from .models import LocalizedProduct, Product, ProductVersie
from .widgets import ProductRadioSelect


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
    publish = forms.ChoiceField(
        choices=PublishChoices.choices, widget=ProductRadioSelect
    )
    date = forms.DateTimeField(required=False)
    beschikbaar = forms.BooleanField(required=False)
    lokaties = forms.ModelMultipleChoiceField(queryset=None, required=False)

    class Meta:
        model = ProductVersie
        fields = (
            "product",
            "gemaakt_door",
            "versie",
            "publicatie_datum",
        )

    @staticmethod
    def _get_version_instance(instance: ProductVersie) -> Optional[ProductVersie]:
        """Decides between updating an existing product version or creating a new version instance.

        - Version is published: create a new version.
        - Version is a concept: update the existing instance.
        - Version is in the future: update the existing instance.
        """
        if instance and instance.get_published_status() == PublishChoices.now:
            return None
        return instance

    def fill_product_data(self, instance: Product) -> bool:
        """Fill product instance with cleaned data
        :returns: A boolean specifying whether a product has changed.
        """
        fields = {"beschikbaar", "lokaties"}
        if not any(True for i in fields if i in self.changed_data):
            return False

        instance.beschikbaar = self.cleaned_data["beschikbaar"]
        instance.lokaties.set(self.cleaned_data["lokaties"])
        return True

    def __init__(self, *args, **kwargs):
        _instance = kwargs.get("instance", None)
        kwargs["instance"] = self._get_version_instance(_instance)
        super().__init__(*args, **kwargs)
        self.fields["beschikbaar"].initial = _instance.product.beschikbaar
        self.fields[
            "lokaties"
        ].queryset = _instance.product.get_municipality_locations()
        self.fields["lokaties"].initial = _instance.product.lokaties.all()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["publish"] == PublishChoices.now:
            cleaned_data["publicatie_datum"] = date.today()
        else:
            cleaned_data["publicatie_datum"] = cleaned_data.get("date", None)

        return cleaned_data

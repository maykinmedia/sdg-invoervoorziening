from typing import Optional

from django import forms

from .constants import PublishChoices
from .models import LocalizedProduct, Product, ProductVersie
from .widgets import CheckboxSelectMultiple


class HelptextMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _model_meta = self._meta.model._meta
        for field in self.fields:
            self.fields[field].help_text = _model_meta.get_field(field).help_text


class LocalizedProductForm(HelptextMixin, forms.ModelForm):

    datum_check = forms.DateTimeField(
        label="Datum check",
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "datum_check",
            "product_titel_decentraal",
            "specifieke_tekst",
            "verwijzing_links",
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


class ProductForm(HelptextMixin, forms.ModelForm):
    product_aanwezig = forms.NullBooleanField(
        required=False,
    )
    product_aanwezig_toelichting = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": "6", "disabled": True}),
    )
    lokaties = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=CheckboxSelectMultiple(),
    )

    class Meta:
        model = Product
        fields = (
            "product_aanwezig",
            "product_aanwezig_toelichting",
            "lokaties",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = self.instance.get_municipality_locations()
        self.fields["lokaties"].queryset = locations
        self.fields["lokaties"].initial = locations.filter(is_product_location=True)


class VersionForm(forms.ModelForm):
    publish = forms.ChoiceField(choices=PublishChoices.choices)
    date = forms.DateTimeField(required=False)

    @staticmethod
    def _get_version_instance(instance: ProductVersie) -> Optional[ProductVersie]:
        """Decides between updating an existing product version or creating a new version instance.

        - Version is published: create a new version.
        - Version is a concept: update the existing instance.
        - Version is in the future: update the existing instance.
        """
        if instance and instance.current_status == Product.status.PUBLISHED:
            return None
        return instance

    class Meta:
        model = ProductVersie
        fields = (
            "product",
            "gemaakt_door",
            "versie",
            "publicatie_datum",
        )

    def __init__(self, *args, **kwargs):
        _instance = kwargs.get("instance", None)
        kwargs["instance"] = self._get_version_instance(_instance)
        super().__init__(*args, **kwargs)
        if _instance.publicatie_datum:
            self.fields["date"].initial = _instance.publicatie_datum.isoformat()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["publish"] == PublishChoices.date:
            cleaned_data["publicatie_datum"] = cleaned_data["date"]
        else:
            cleaned_data["publicatie_datum"] = None

        return cleaned_data

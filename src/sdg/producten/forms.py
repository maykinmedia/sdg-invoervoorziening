from typing import Optional

from django import forms
from django.forms import inlineformset_factory

from ..core.models.mixins import FieldConfigurationMixin
from .constants import PublishChoices
from .models import LocalizedProduct, Product, ProductVersie
from .widgets import CheckboxSelectMultiple


class LocalizedProductForm(FieldConfigurationMixin, forms.ModelForm):
    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "product_titel_decentraal",
            "specifieke_tekst",
            "verwijzing_links",
            "procedure_beschrijving",
            "vereisten",
            "bewijs",
            "bezwaar_en_beroep",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "wtd_bij_geen_reactie",
            "decentrale_procedure_link",
            "product_valt_onder_toelichting",
        )


class LocalizedProductFormSet(
    inlineformset_factory(
        ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=0
    )
):
    def __init__(self, *args, **kwargs):
        self._product_form = kwargs.pop("product_form", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        - Ensure all localized `product_valt_onder_toelichting` fields are filled
          if `product_valt_onder` is filled.
        """
        cleaned_data = super().clean()
        if self._product_form.cleaned_data.get("product_valt_onder"):
            for form in self.forms:
                if not form.cleaned_data.get("product_valt_onder_toelichting"):
                    form.add_error(
                        "product_valt_onder_toelichting",
                        "Vul de toelichting in als het product valt onder.",
                    )
        return cleaned_data


class ProductForm(FieldConfigurationMixin, forms.ModelForm):
    product_aanwezig = forms.NullBooleanField(
        required=False,
    )
    product_aanwezig_toelichting = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": "6", "disabled": True}),
    )
    product_valt_onder = forms.ModelChoiceField(
        queryset=Product.objects.filter(
            referentie_product__isnull=False,
        ).annotate_name(),
        required=False,
    )
    locaties = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=CheckboxSelectMultiple(),
    )

    class Meta:
        model = Product
        fields = (
            "product_aanwezig",
            "product_aanwezig_toelichting",
            "product_valt_onder",
            "locaties",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = self.instance.get_municipality_locations()
        self.fields["locaties"].queryset = locations
        self.fields["locaties"].initial = locations.filter(is_product_location=True)
        self.fields["product_valt_onder"].queryset = (
            self.fields["product_valt_onder"]
            .queryset.filter(catalogus=self.instance.catalogus)
            .exclude(pk=self.instance.pk)
        )

        _model_meta = self._meta.model._meta
        for field in self.fields:
            self.fields[field].help_text = _model_meta.get_field(field).help_text

    def clean(self):
        cleaned_data = super().clean()
        product_aanwezig = cleaned_data.get("product_aanwezig")
        product_aanwezig_toelichting = cleaned_data.get("product_aanwezig_toelichting")

        if product_aanwezig is False and not product_aanwezig_toelichting:
            self.add_error("product_aanwezig_toelichting", "Dit veld is verplicht.")

        return cleaned_data


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

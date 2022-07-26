from datetime import date
from typing import Optional

from django import forms
from django.forms import inlineformset_factory
from django.db.models import F, CharField, Value, Case, When, Count
from django.db.models.functions import Concat

from ..core.models.mixins import FieldConfigurationMixin
from ..organisaties.models import BevoegdeOrganisatie
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
            "vereisten",
            "bewijs",
            "procedure_beschrijving",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "bezwaar_en_beroep",
            "wtd_bij_geen_reactie",
            "verwijzing_links",
            "decentrale_procedure_link",
            "product_valt_onder_toelichting",
            "product_aanwezig_toelichting",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_fields()


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

        if self._product_form.cleaned_data is not None:
            for form in self.forms:
                if self._product_form.cleaned_data.get(
                    "product_aanwezig"
                ) is False and not form.cleaned_data.get(
                    "product_aanwezig_toelichting"
                ):
                    form.add_error(
                        "product_aanwezig_toelichting", "Dit veld is verplicht."
                    )

        return cleaned_data


class ProductForm(FieldConfigurationMixin, forms.ModelForm):
    product_aanwezig = forms.NullBooleanField(
        required=False,
    )
    product_valt_onder = forms.ModelChoiceField(
        queryset=Product.objects.filter(
            referentie_product__isnull=False,
        ).annotate_name(),
        required=False,
    )
    bevoegde_organisatie = forms.ModelChoiceField(
        queryset=BevoegdeOrganisatie.objects.all(),
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
            "product_valt_onder",
            "bevoegde_organisatie",
            "locaties",
        )

    def _help_text(self, field):
        return Product._meta.get_field(field).help_text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = self.instance.get_municipality_locations()
        duplicates_generiek_product_upn_labels = (
            Product.objects.filter(
                catalogus=self.instance.catalogus,
                referentie_product__isnull=False,
            )
            .values("generiek_product__upn__upn_label")
            .annotate(count=Count("id"))
            .values("generiek_product__upn__upn_label")
            .order_by()
            .filter(count__gt=1)
        )
        self.fields["locaties"].queryset = locations
        self.fields["locaties"].initial = locations.filter(is_product_location=True)
        self.fields["product_valt_onder"].queryset = (
            self.fields["product_valt_onder"]
            .queryset.filter(catalogus=self.instance.catalogus)
            .annotate(
                _name=Case(
                    When(
                        generiek_product__upn__upn_label__in=[
                            item["generiek_product__upn__upn_label"]
                            for item in duplicates_generiek_product_upn_labels
                        ],
                        then=Concat(
                            F("generiek_product__upn__upn_label"),
                            Value(" - "),
                            F("generiek_product__doelgroep"),
                            output_field=CharField(),
                        ),
                    ),
                    default=F("generiek_product__upn__upn_label"),
                )
            )
            .exclude(pk=self.instance.pk)
        )
        self.fields["bevoegde_organisatie"].queryset = self.fields[
            "bevoegde_organisatie"
        ].queryset.filter(lokale_overheid=self.instance.catalogus.lokale_overheid)

        for field in self.fields:
            self.fields[field].help_text = self._help_text(field)

        self.configure_fields()


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
        self.product_instance = kwargs.pop("product_instance", None)
        kwargs["instance"] = self._get_version_instance(_instance)
        super().__init__(*args, **kwargs)
        if _instance.publicatie_datum:
            if _instance.publicatie_datum > date.today():
                self.fields["date"].initial = _instance.publicatie_datum.isoformat()
            else:
                self.fields["date"].initial = str(date.today())

    def clean(self):
        cleaned_data = super().clean()

        if not self.cleaned_data["product"] and self.product_instance:
            self.cleaned_data["product"] = self.product_instance

        if cleaned_data["publish"] == PublishChoices.date:
            cleaned_data["publicatie_datum"] = cleaned_data["date"]
        else:
            cleaned_data["publicatie_datum"] = None

        return cleaned_data

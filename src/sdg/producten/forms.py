from datetime import date
from typing import Optional

from django import forms
from django.conf import settings
from django.db.models import Case, CharField, Count, F, Q, Value, When
from django.db.models.functions import Concat
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from ..core.forms import BooleanChoiceField
from ..core.models.mixins import FieldConfigurationMixin
from ..organisaties.models import BevoegdeOrganisatie
from ..utils.validators import validate_placeholders
from .constants import PublishChoices
from .models import LocalizedProduct, Product, ProductVersie
from .utils import get_placeholder_maps, parse_changed_data
from .widgets import CheckboxSelectMultiple


class LocalizedProductForm(FieldConfigurationMixin, forms.ModelForm):
    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "product_valt_onder_toelichting",
            "product_aanwezig_toelichting",
            *settings.SDG_LOCALIZED_FORM_FIELDS,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_fields(self.instance.taal)


class LocalizedProductFormSet(
    inlineformset_factory(
        ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=0
    )
):
    def __init__(self, *args, **kwargs):
        self._product_form = kwargs.pop("product_form", None)
        super().__init__(*args, **kwargs)

        if self._product_form:
            (
                available_explanation_map,
                falls_under_explanation_map,
            ) = get_placeholder_maps(self._product_form.instance)

            self.title = f"Standaardtekst v{self.instance.versie} ({self.instance.publicatie_datum or 'concept'})"
            for form in self.forms:
                form.default_toelichting = available_explanation_map.get(
                    form.instance.taal
                )
                form.default_product_aanwezig_toelichting = (
                    falls_under_explanation_map.get(form.instance.taal)
                )

        else:
            for form in self.forms:
                if not form.initial["product_titel_decentraal"]:
                    form.initial["product_titel_decentraal"] = (
                        self.instance.product.generiek_product.vertalingen.get(
                            taal=form.instance.taal
                        ).product_titel
                    )

    def clean(self):
        """
        - Ensure all localized `product_valt_onder_toelichting` fields are filled
          if `product_valt_onder` is filled.
        """
        cleaned_data = super().clean()

        is_reference = self.instance.product.is_referentie_product

        falls_under = self._product_form.cleaned_data.get("product_valt_onder")
        available = self._product_form.cleaned_data.get("product_aanwezig")

        available_explanation_map, falls_under_explanation_map = get_placeholder_maps(
            self.instance.product
        )

        for form in self.forms:
            cleaned_data = form.cleaned_data
            language = cleaned_data["taal"]

            available_explanation = cleaned_data.get("product_aanwezig_toelichting")
            falls_under_explanation = cleaned_data.get("product_valt_onder_toelichting")

            if falls_under and not falls_under_explanation:
                form.add_error(
                    "product_valt_onder_toelichting",
                    "Vul de toelichting in als het product valt onder.",
                )

            if available is False and not available_explanation:
                form.add_error("product_aanwezig_toelichting", "Dit veld is verplicht.")

            if falls_under_explanation == falls_under_explanation_map.get(language):
                form.instance.product_valt_onder_toelichting = ""

            if available_explanation == available_explanation_map.get(language):
                form.instance.product_aanwezig_toelichting = ""

            if not is_reference:
                self._validate_specific(form)

        return cleaned_data

    def _validate_specific(self, form):
        """
        Validate only for localized specific product.
        """
        if self.data.get("publish") != PublishChoices.date:  # only published
            return

        cleaned_data = list(form.cleaned_data.items())
        for name, value in cleaned_data:
            validate_placeholders(value, form=form, field_name=name)

    @property
    def changed_data_localized(self):
        result = []
        for form in self.forms:
            result.extend(
                parse_changed_data(
                    form.changed_data,
                    form=form,
                    language=form.instance.taal,
                )
            )
        return result


class ProductForm(FieldConfigurationMixin, forms.ModelForm):
    product_aanwezig = forms.NullBooleanField(
        required=False,
    )
    product_valt_onder = forms.ModelChoiceField(
        queryset=Product.objects.filter(
            referentie_product__isnull=False,
        )
        .annotate_name()
        .exclude_generic_status(),
        required=False,
    )
    bevoegde_organisatie = forms.ModelChoiceField(
        queryset=BevoegdeOrganisatie.objects.all(),
        required=False,
        empty_label=None,
    )
    locaties = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=CheckboxSelectMultiple(),
    )
    heeft_kosten = BooleanChoiceField()
    api_verborgen = BooleanChoiceField(
        label=_("verborgen"),
    )

    class Meta:
        model = Product
        fields = (
            "product_aanwezig",
            "product_valt_onder",
            "bevoegde_organisatie",
            "locaties",
            "heeft_kosten",
            "api_verborgen",
        )

    def _help_text(self, field):
        return Product._meta.get_field(field).help_text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.product_valt_onder:
            selected_product = self.instance.product_valt_onder.generiek_product
        else:
            selected_product = None

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
            .queryset.filter(
                Q(
                    generiek_product=selected_product,
                    catalogus=self.instance.catalogus,
                )
                | Q(
                    generiek_product__doelgroep=self.instance.generiek_product.doelgroep,
                    catalogus=self.instance.catalogus,
                )
            )
            .annotate(
                _name=Case(
                    When(
                        ~Q(generiek_product__doelgroep=""),
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

        if self.initial["product_aanwezig"] is None:
            self.initial["product_aanwezig"] = True

        for field in self.fields:
            self.fields[field].help_text = self._help_text(field)

        self.configure_fields()

    def clean(self):
        cleaned_data = super().clean()

        available = cleaned_data.get("product_aanwezig")
        is_reference = self.instance.is_referentie_product

        if not is_reference:
            if "date" in self.data.get("publish"):
                if available is None:

                    self.add_error(
                        "product_aanwezig",
                        "Je hebt nog niet aangegeven of jouw gemeente dit product aanbiedt. \
                        Geef dit aan met Ja of Nee. Let op! \
                        Je kan deze pagina alleen publiceren als je een keuze hebt gemaakt.",
                    )


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
            "interne_opmerkingen",
            "bewerkte_velden",
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

        if (
            self.product_instance.most_recent_version.publicatie_datum
            and self.product_instance.most_recent_version.publicatie_datum
            <= date.today()
        ):
            cleaned_data["versie"] = (
                self.product_instance.most_recent_version.versie + 1
            )

        if cleaned_data["publish"] == PublishChoices.date:
            if cleaned_data["date"].date() < date.today():
                raise forms.ValidationError(
                    _("De publicatiedatum kan niet in het verleden liggen.")
                )
            cleaned_data["publicatie_datum"] = cleaned_data["date"]
        else:
            cleaned_data["publicatie_datum"] = None

        for name, value in list(cleaned_data.items()):
            if cleaned_data.get("publish") == PublishChoices.date:
                validate_placeholders(value, form=self, field_name=name)

        return cleaned_data

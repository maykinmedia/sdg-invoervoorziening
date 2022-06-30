from itertools import zip_longest
from typing import Tuple

from django.db import transaction
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.constants import TaalChoices
from sdg.core.types import Event
from sdg.producten.forms import (
    LocalizedProductForm,
    LocalizedProductFormSet,
    ProductForm,
    VersionForm,
)
from sdg.producten.models import LocalizedProduct, Product, ProductVersie
from sdg.producten.utils import build_url_kwargs, duplicate_localized_products


class ProductPreviewView(OverheidMixin, DetailView):
    template_name = "mocks/kvk.html"
    context_object_name = "product"
    pk_url_kwarg = "product_pk"
    required_roles = ["is_beheerder", "is_redacteur"]

    def is_concept(self):
        if self.request.GET.get("status", "") == "concept":
            return True

        return False

    def get_queryset(self):
        if self.is_concept():
            return (
                Product.objects.select_related("catalogus__lokale_overheid")
                .prefetch_related(
                    "locaties",
                    Prefetch(
                        "referentie_product", queryset=Product.objects.most_recent()
                    ),
                )
                .most_recent()
                .active()
            )
        else:
            return (
                Product.objects.select_related("catalogus__lokale_overheid")
                .prefetch_related(
                    "locaties",
                    Prefetch("referentie_product", queryset=Product.objects.active()),
                )
                .active()
            )

    def get_lokale_overheid(self):
        self.object = self.get_object()

        if self.is_concept():
            self.lokale_overheid = (
                self.object.most_recent_version.product.catalogus.lokale_overheid
            )
        else:
            self.lokale_overheid = (
                self.object.active_version.product.catalogus.lokale_overheid
            )

        self.lokale_overheid = self.object.catalogus.lokale_overheid

        return self.lokale_overheid

    def _get_generieke_taal_producten(self):
        required_fields = ["verwijzing_links", "datum_check"]

        nl = self.object.generiek_product.vertalingen.filter(taal="nl").first()
        en = self.object.generiek_product.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_algemene_taal_producten(self):
        required_fields = [
            "product_aanwezig_toelichting",
            "product_valt_onder_toelichting",
        ]
        if self.is_concept():
            nl = self.object.most_recent_version.vertalingen.filter(taal="nl").first()
            en = self.object.most_recent_version.vertalingen.filter(taal="en").first()
        else:
            nl = self.object.active_version.vertalingen.filter(taal="nl").first()
            en = self.object.active_version.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_specifieke_taal_producten(self):
        required_fields = [
            "vereisten",
            "bewijs",
            "procedure_beschrijving",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "bezwaar_en_beroep",
            "wtd_bij_geen_reactie",
            "decentrale_procedure_link",
        ]

        if self.is_concept():
            nl = self.object.most_recent_version.vertalingen.filter(taal="nl").first()
            en = self.object.most_recent_version.vertalingen.filter(taal="en").first()
        else:
            nl = self.object.active_version.vertalingen.filter(taal="nl").first()
            en = self.object.active_version.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = list(TaalChoices.labels.keys())
        context["product"] = self.object
        context["locale_overheid"] = self.object.catalogus.lokale_overheid

        context["product_locaties"] = self.object.locaties.all()

        context["generieke_producten"] = self._get_generieke_taal_producten()
        context["algemene_producten"] = self._get_algemene_taal_producten()
        context["specifieke_producten"] = self._get_specifieke_taal_producten()

        context["days"] = [
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        ]

        return context


class ProductUpdateView(OverheidMixin, UpdateView):
    template_name = "producten/update.html"
    context_object_name = "product_versie"
    pk_url_kwarg = "product_pk"
    form_class = LocalizedProductFormSet
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_queryset(self):
        return (
            Product.objects.most_recent()
            .active()
            .select_related("catalogus__lokale_overheid")
        )

    def _save_version_form(self, version_form) -> Tuple[ProductVersie, bool]:
        """Save the version form.
        Return a tuple of (version object, created), where created is a boolean
        specifying whether an object was created.
        """
        new_version = version_form.save(commit=False)

        created = self.object != new_version
        new_version.product = self.product
        new_version.gemaakt_door = self.request.user
        new_version.versie = self.object.versie + 1 if created else self.object.versie
        new_version.save()
        return new_version, created

    def _generate_version_formset(self, version: ProductVersie):
        product_nl = self.product.generiek_product.vertalingen.get(taal="nl")
        product_en = self.product.generiek_product.vertalingen.get(taal="en")

        default_explanation_mapping = {
            "nl": f"In de gemeente {self.lokale_overheid} valt het product {product_nl} onder het product [product].",
            "en": f"In the municipality of {self.lokale_overheid}, the product {product_en} falls under the product [product].",
        }

        default_aanwezig_toelichting_explanation_mapping = {
            "nl": f"De gemeente {self.lokale_overheid} levert het product {product_nl} niet omdat...",
            "en": f"The municipality of {self.lokale_overheid} doesn't offer {product_en} because...",
        }
        formset = inlineformset_factory(
            ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=0
        )(instance=version)
        formset.title = f"Standaardtekst v{version.versie} ({version.publicatie_datum if version.publicatie_datum else 'concept'})"
        for form in formset:
            form.default_toelichting = default_explanation_mapping.get(
                form.instance.taal
            )

            form.default_product_aanwezig_toelichting = (
                default_aanwezig_toelichting_explanation_mapping.get(form.instance.taal)
            )

        return formset

    def _get_generieke_taal_producten(self):
        required_fields = [
            "product_titel",
            "generieke_tekst",
            "datum_check",
            "verwijzing_links",
        ]
        nl = self.product.generiek_product.vertalingen.filter(taal="nl").first()
        en = self.product.generiek_product.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def get_lokale_overheid(self):
        self.product = self.get_object()
        self.lokale_overheid = self.product.catalogus.lokale_overheid
        self.object = self.product.most_recent_version
        return self.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generic_information = self.product.generiek_product.vertalingen.all()

        context["generic_products"] = self._get_generieke_taal_producten()

        context["button_information"] = _(
            "'Opslaan als concept' slaat het product op zonder te publiceren zodat u er later nog aan kan werken.\n'Opslaan en publiceren' maakt een nieuwe gepubliceerde versie van het product aan, actief vanaf de gekozen datum aan de linkerkant."
        )

        context["languages"] = list(TaalChoices.labels.keys())
        context["product"] = self.product
        context["lokaleoverheid"] = self.product.catalogus.lokale_overheid

        context["reference_formset"] = self._generate_version_formset(
            version=self.product.reference_product.most_recent_version
        )
        context["previous_reference_formset"] = self._generate_version_formset(
            self.product.reference_product.get_latest_versions(2)[-1]  # TODO: optimize
        )
        context["formset"] = context["form"]
        context["informatie_forms"] = zip_longest(
            generic_information, context["form"].forms
        )

        context["version_form"] = kwargs.get(
            "version_form",
            VersionForm(instance=self.object, product_instance=self.product),
        )
        context["product_form"] = kwargs.get(
            "product_form", ProductForm(instance=self.product)
        )

        context["history"] = self.product.get_all_versions()

        # FIXME: Optimize?
        context["localized_form_fields"] = [
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
        ]
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST, instance=self.product)
        version_form = VersionForm(
            request.POST, instance=self.object, product_instance=self.product
        )
        form = self.form_class(
            request.POST,
            instance=self.object,
            product_form=product_form,
        )

        forms = (product_form, version_form, form)
        forms_valid = [f.is_valid() for f in forms]
        if not all(forms_valid):
            return self.form_invalid(*forms)

        return self.form_valid(*forms)

    def form_valid(self, product_form, version_form, form):
        with transaction.atomic():
            product_form.save()
            new_version, created = self._save_version_form(version_form)
            if created:
                Event.create_and_log(self.request, self.object, Event.CREATE)
                duplicate_localized_products(form, new_version)
            else:
                Event.create_and_log(self.request, self.object, Event.UPDATE)
                form.save()
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, product_form, version_form, form):
        context = self.get_context_data(
            form=form, version_form=version_form, product_form=product_form
        )
        context["form_invalid"] = True
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse(
            "organisaties:catalogi:producten:edit",
            kwargs=build_url_kwargs(self.product),
        )

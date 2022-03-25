from itertools import zip_longest
from typing import Tuple

from django.db import transaction
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.mixins import OverheidMixin
from sdg.core.models import ProductenCatalogus
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

    def get_queryset(self):
        return (
            Product.objects.select_related("catalogus__lokale_overheid")
            .prefetch_related(
                "locaties",
                Prefetch("referentie_product", queryset=Product.objects.most_recent()),
            )
            .most_recent()
            .active()
        )

    def get_lokale_overheid(self):
        self.object = self.get_object()
        self.lokale_overheid = self.object.catalogus.lokale_overheid
        return self.lokale_overheid

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        context["lokaleoverheid"] = self.lokale_overheid
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taal = self.request.GET.get("taal", "nl")
        context["translation"] = self.object.active_version.vertalingen.get(taal=taal)
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
        default_explanation_mapping = {
            "nl": f"In de gemeente {self.lokale_overheid} valt het product {self.product} onder het product [product].",
            "en": f"In the municipality of {self.lokale_overheid}, the product {self.product} falls under the product [product].",
        }
        formset = inlineformset_factory(
            ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=0
        )(instance=version)
        formset.title = f"Standaardtekst v{version.versie} ({version.publicatie_datum if version.publicatie_datum else 'concept'})"
        for form in formset:
            form.default_toelichting = default_explanation_mapping.get(
                form.instance.taal
            )
        return formset

    def get_lokale_overheid(self):
        self.product = self.get_object()
        self.lokale_overheid = self.product.catalogus.lokale_overheid
        self.object = self.product.most_recent_version
        return self.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generic_information = self.product.generic_product.vertalingen.all()

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
            "version_form", VersionForm(instance=self.object)
        )
        context["product_form"] = kwargs.get(
            "product_form", ProductForm(instance=self.product)
        )

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
            "product_valt_onder_toelichting",
        ]
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST, instance=self.product)
        version_form = VersionForm(request.POST, instance=self.object)
        form = self.form_class(
            request.POST, instance=self.object, product_form=product_form
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

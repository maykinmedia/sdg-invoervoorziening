from itertools import zip_longest
from typing import Optional, Tuple

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.mixins import OverheidMixin
from sdg.core.models import ProductenCatalogus
from sdg.producten.constants import PublishChoices
from sdg.producten.forms import LocalizedProductForm, ProductVersionForm
from sdg.producten.models import (
    GeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)
from sdg.producten.utils import duplicate_localized_products


class ProductCreateRedirectView(SingleObjectMixin, RedirectView):
    """
    Get or create (children) specific product if this is a reference product.
    Redirect to product detail view.
    """

    context_object_name = "product"
    model = Product

    def get(self, request, *args, **kwargs):
        obj = super().get_object()

        if kwargs.get("catalog_pk"):
            catalog = get_object_or_404(ProductenCatalogus, pk=kwargs["catalog_pk"])
            if catalog.user_is_redacteur(self.request.user):
                obj = obj.get_or_create_specific_product(specific_catalog=catalog)
            else:
                raise PermissionDenied()

        kwargs["obj"] = obj
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("producten:detail", kwargs={"pk": kwargs.get("obj").pk})


class ProductDetailView(OverheidMixin, DetailView):
    template_name = "producten/product_detail.html"
    context_object_name = "product"
    queryset = Product.objects.select_related(
        "catalogus__lokale_overheid"
    ).prefetch_related(
        "lokaties",
        "versies__vertalingen",
        "referentie_product__versies__vertalingen",
        Prefetch(
            "referentie_product__generiek_product",
            queryset=GeneriekProduct.objects.prefetch_related("vertalingen"),
        ),
    )
    required_roles = ["is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        self.lokale_overheid = self.object.catalogus.lokale_overheid
        return self.lokale_overheid

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ProductUpdateView(OverheidMixin, UpdateView):
    template_name = "producten/product_edit.html"
    context_object_name = "product_versie"
    queryset = Product.objects.select_related("catalogus__lokale_overheid")
    form_class = inlineformset_factory(
        ProductVersie,
        LocalizedProduct,
        form=LocalizedProductForm,
        extra=0,
    )
    required_roles = ["is_redacteur"]

    def _save_version_form(self, version_form) -> Tuple[ProductVersie, bool]:
        """
        Saves the version form.
        Return a tuple of (version object, created), where created is a boolean
        specifying whether an object was created.
        """
        with transaction.atomic():
            new_version = version_form.save(commit=False)

            created = self.object != new_version
            new_version.product = self.product
            new_version.gemaakt_door = self.request.user
            new_version.versie = (
                self.object.versie + 1 if created else self.object.versie
            )
            new_version.save()

            if "beschikbaar" in version_form.changed_data:
                new_version.product.beschikbaar = version_form.cleaned_data[
                    "beschikbaar"
                ]
                new_version.product.save()

            return new_version, created

    def get_lokale_overheid(self):
        self.product = self.get_object()
        self.lokale_overheid = self.product.catalogus.lokale_overheid
        self.object = self.product.laatste_versie
        return self.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generic_information = self.product.generic_product.vertalingen.all()

        # TODO: simplify
        if self.product.is_referentie_product:
            reference_product = self.product
        else:
            reference_product = self.product.referentie_product
        reference_formset = inlineformset_factory(
            ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=0
        )(instance=reference_product.laatste_versie)

        context["product"] = self.product
        context["lokale_overheid"] = self.product.catalogus.lokale_overheid

        context["reference_forms"] = reference_formset.forms
        context["informatie_forms"] = zip_longest(
            generic_information, context["form"].forms
        )
        context["version_form"] = kwargs.get("version_form") or ProductVersionForm(
            instance=self.object
        )
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        version_form = ProductVersionForm(request.POST, instance=self.object)

        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid() and version_form.is_valid():
            return self.form_valid(form, version_form)
        else:
            return self.form_invalid(form, version_form)

    def form_valid(self, form, version_form):
        new_version, created = self._save_version_form(version_form)
        if created:
            duplicate_localized_products(form, new_version)
        else:
            form.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, version_form):
        return self.render_to_response(
            self.get_context_data(form=form, version_form=version_form)
        )

    def get_success_url(self):
        return reverse("producten:detail", kwargs={"pk": self.product.pk})

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
from sdg.producten.forms import LocalizedProductForm, ProductForm, ProductVersionForm
from sdg.producten.models import LocalizedProduct, Product, ProductVersie
from sdg.producten.utils import build_url_kwargs, duplicate_localized_products


class ProductCreateRedirectView(OverheidMixin, SingleObjectMixin, RedirectView):
    """
    Get or create (children) specific product if this is a reference product.
    Redirect to product detail view.
    """

    context_object_name = "product"
    pk_url_kwarg = "product_pk"
    queryset = Product.objects.select_related(
        "catalogus__lokale_overheid",
    )

    def get_lokale_overheid(self):
        self.object = self.get_object()
        self.catalog = ProductenCatalogus.objects.select_related(
            "lokale_overheid",
        ).get(pk=self.kwargs["catalog_pk"])
        return self.catalog.lokale_overheid

    def get(self, request, *args, **kwargs):
        product = self.object.get_or_create_specific_product(
            specific_catalog=self.catalog
        )
        kwargs["product"] = product
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "organisaties:catalogi:producten:detail",
            kwargs=build_url_kwargs(kwargs["product"], catalog=self.catalog),
        )


class ProductDetailView(OverheidMixin, DetailView):
    template_name = "producten/detail.html"
    context_object_name = "product"
    pk_url_kwarg = "product_pk"
    queryset = (
        Product.objects.select_related("catalogus__lokale_overheid")
        .prefetch_related(
            "lokaties",
            Prefetch("referentie_product", queryset=Product.objects.most_recent()),
        )
        .most_recent()
        .active()
    )
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        self.lokale_overheid = self.object.catalogus.lokale_overheid
        return self.lokale_overheid

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        context["lokaleoverheid"] = self.lokale_overheid
        return self.render_to_response(context)


class ProductUpdateView(OverheidMixin, UpdateView):
    template_name = "producten/edit.html"
    context_object_name = "product_versie"
    pk_url_kwarg = "product_pk"
    queryset = Product.objects.most_recent().select_related(
        "catalogus__lokale_overheid"
    )
    form_class = inlineformset_factory(
        ProductVersie,
        LocalizedProduct,
        form=LocalizedProductForm,
        extra=0,
    )
    required_roles = ["is_beheerder", "is_redacteur"]

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
        formset = inlineformset_factory(
            ProductVersie, LocalizedProduct, form=LocalizedProductForm, extra=1
        )(instance=version)
        formset.title = f"v{version.versie} ({version.publicatie_datum})"
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
            self.product.reference_product.get_latest_versions(2)[0]  # TODO: optimize
        )

        context["informatie_forms"] = zip_longest(
            generic_information, context["form"].forms
        )
        context["product_form"] = kwargs.get("product_form") or ProductForm(
            instance=self.product
        )
        context["version_form"] = kwargs.get("version_form") or ProductVersionForm(
            instance=self.object
        )

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        version_form = ProductVersionForm(request.POST, instance=self.object)
        product_form = ProductForm(request.POST, instance=self.product)
        form = self.form_class(request.POST, instance=self.object)

        if form.is_valid() and version_form.is_valid() and product_form.is_valid():
            return self.form_valid(form, version_form, product_form)
        else:
            return self.form_invalid(form, version_form, product_form)

    def form_valid(self, form, version_form, product_form):
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

    def form_invalid(self, form, version_form, product_form):
        return self.render_to_response(
            self.get_context_data(
                form=form, version_form=version_form, product_form=product_form
            )
        )

    def get_success_url(self):
        return reverse(
            "organisaties:catalogi:producten:detail",
            kwargs=build_url_kwargs(self.product),
        )

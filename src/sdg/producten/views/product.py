from itertools import zip_longest

from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.core.models import ProductenCatalogus
from sdg.producten.forms import LocalizedProductForm
from sdg.producten.models import GeneriekProduct, LocalizedProduct, Product


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


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    context_object_name = "product"
    queryset = Product.objects.select_related(
        "catalogus__lokale_overheid"
    ).prefetch_related(
        "lokaties",
        "vertalingen",
        "referentie_product__vertalingen",
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


class ProductUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"
    context_object_name = "product"
    queryset = Product.objects.select_related("catalogus__lokale_overheid")
    form_class = inlineformset_factory(
        Product,
        LocalizedProduct,
        form=LocalizedProductForm,
        extra=0,
    )
    required_roles = ["is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object.catalogus.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generic_information = self.object.get_generic_product().vertalingen.all()
        reference_formset = inlineformset_factory(
            Product, LocalizedProduct, form=LocalizedProductForm, extra=0
        )(
            instance=self.object.referentie_product,
        )
        context["informatie_form"] = zip_longest(
            generic_information, reference_formset.forms, context["form"].forms
        )
        context["lokale_overheid"] = self.object.catalogus.lokale_overheid
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("producten:detail", kwargs={"pk": self.object.pk})

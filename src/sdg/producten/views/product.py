from itertools import zip_longest

from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.models import GeneriekProduct, LocalizedProduct, Product
from sdg.producten.views import BaseProductUpdateView
from sdg.producten.views.mixins import OptionalFormMixin


class ProductCreateRedirectView(SingleObjectMixin, RedirectView):
    """
    Get or create (children) specific product if this is a reference product.
    Redirect to product detail view.
    """

    context_object_name = "product"
    model = Product

    def get(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.is_reference_product():
            obj = obj.get_or_create_specific_product()

        kwargs["obj"] = obj
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("producten:detail", kwargs={"pk": kwargs.get("obj").pk})


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    context_object_name = "product"
    queryset = Product.objects.prefetch_related(
        "lokaties",
        "vertalingen",
        "referentie_product__vertalingen",
        Prefetch(
            "referentie_product__generiek_product",
            queryset=GeneriekProduct.objects.prefetch_related("vertalingen"),
        ),
    )
    model = Product

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.is_reference_product():
            return redirect(
                reverse("producten:redirect", kwargs={"pk": self.object.pk})
            )

        return response


# TODO: Refactor mixins
class ProductUpdateView(
    OptionalFormMixin, OverheidRoleRequiredMixin, BaseProductUpdateView
):
    template_name = "producten/product_edit.html"
    parent_model = Product
    child_model = LocalizedProduct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = context["product"]
        generic_information = product.get_generic_product().vertalingen.all()
        context["informatie_form"] = zip_longest(
            generic_information, context["form"].forms
        )

        return context

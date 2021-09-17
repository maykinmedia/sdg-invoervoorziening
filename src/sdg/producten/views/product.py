from itertools import zip_longest

from django.urls import reverse
from django.views.generic import DetailView, RedirectView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.models import ProductSpecifiekInformatie, SpecifiekProduct
from sdg.producten.views import BaseProductUpdateView
from sdg.producten.views.mixins import OptionalFormMixin


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    context_object_name = "product"
    queryset = SpecifiekProduct.objects.all().prefetch_related(
        "referentie__generiek__informatie",
        "informatie",
        "lokaties",
    )
    model = SpecifiekProduct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_information = context["product"].informatie.all()
        generic_information = context["product"].referentie.generiek.informatie.all()

        context["informatie"] = zip_longest(generic_information, product_information)

        return context


class ProductUpdateView(
    OptionalFormMixin, OverheidRoleRequiredMixin, BaseProductUpdateView
):
    template_name = "producten/product_edit.html"
    parent_model = SpecifiekProduct
    child_model = ProductSpecifiekInformatie

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        generic_information = context["product"].referentie.generiek.informatie.all()
        context["informatie_form"] = zip_longest(
            generic_information, context["form"].forms
        )

        return context


class CreateProductRedirectView(RedirectView):
    def get(self, request, *args, **kwargs):
        # TODO: Create product from C to C1
        self.created_pk = ...
        super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("producten:edit", kwargs={"pk": kwargs.get(self.created_pk)})

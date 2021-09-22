from itertools import zip_longest

from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.forms import GegevensFormHelper, ProductGegevensForm
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

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object.catalogus.lokale_overheid

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)

        if self.object.is_reference_product():
            return redirect(
                reverse("producten:redirect", kwargs={"pk": self.object.pk})
            )
        else:
            return self.render_to_response(context)

class ProductUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"
    context_object_name = "product"
    model = Product
    child_model = LocalizedProduct
    form_class = inlineformset_factory(
        Product,
        LocalizedProduct,
        form=ProductGegevensForm,
        extra=0,
    )

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object.catalogus.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generic_information = self.object.get_generic_product().vertalingen.all()
        context["informatie_form"] = zip_longest(
            generic_information, context["form"].forms
        )
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

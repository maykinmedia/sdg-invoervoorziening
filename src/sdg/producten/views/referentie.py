from itertools import zip_longest

from django.views.generic import DetailView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.models import ProductReferentieInformatie, ReferentieProduct
from sdg.producten.views import BaseProductUpdateView


class ReferentieProductDetailView(RootEditorRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    context_object_name = "product"
    model = ReferentieProduct
    queryset = ReferentieProduct.objects.all().prefetch_related(
        "generiek__informatie",
        "informatie",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        referentie_information = context["product"].informatie.all()
        generic_information = context["product"].generiek.informatie.all()

        # Zip without generic information
        context["informatie"] = zip_longest(generic_information, referentie_information)

        return context

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ReferentieProductUpdateView(RootEditorRequiredMixin, BaseProductUpdateView):
    template_name = "producten/product_edit.html"
    parent_model = ReferentieProduct
    child_model = ProductReferentieInformatie

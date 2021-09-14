from django.views import View
from django.views.generic import DetailView, FormView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import ProductReferentieInformatieFormset
from sdg.producten.models import ReferentieProduct


class ReferentieProductDetailView(RootEditorRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = ReferentieProduct
    queryset = ReferentieProduct.objects.prefetch_related(
        "informatie",
    ).all()

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ReferentieProductUpdateView(RootEditorRequiredMixin, FormView):
    template_name = "producten/product_edit.html"

    model = ReferentieProduct
    form_class = ProductReferentieInformatieFormset

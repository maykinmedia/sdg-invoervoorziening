from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import ProductReferentieInformatie


class ReferentieProductDetailView(RootEditorRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"

    model = ProductReferentieInformatie

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ReferentieProductUpdateView(RootEditorRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"

    model = ProductReferentieInformatie
    form_class = ProductSpecifiekInformatieForm

from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import StandaardProductSpecifiekInformatie


class StandaardProductDetailView(RootEditorRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"

    model = StandaardProductSpecifiekInformatie

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class StandaardProductUpdateView(RootEditorRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"

    model = StandaardProductSpecifiekInformatie
    form_class = ProductSpecifiekInformatieForm

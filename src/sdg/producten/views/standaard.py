from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import StandaardProductSpecifiekInformatie


class StandaardMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["standaard"] = True
        return context


class StandaardProductDetailView(RootEditorRequiredMixin, StandaardMixin, DetailView):
    model = StandaardProductSpecifiekInformatie


class StandaardProductUpdateView(RootEditorRequiredMixin, StandaardMixin, UpdateView):
    template_name = "producten/product_edit.html"

    model = StandaardProductSpecifiekInformatie
    form_class = ProductSpecifiekInformatieForm

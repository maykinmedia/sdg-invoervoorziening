from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import StandaardProductSpecifiekInformatie
from sdg.producten.views.mixins import StandaardMixin


class StandaardProductDetailView(RootEditorRequiredMixin, StandaardMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = StandaardProductSpecifiekInformatie


class StandaardProductUpdateView(RootEditorRequiredMixin, StandaardMixin, UpdateView):
    template_name = "producten/product_edit.html"

    model = StandaardProductSpecifiekInformatie
    form_class = ProductSpecifiekInformatieForm

from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import ProductSpecifiekInformatie
from sdg.producten.views.mixins import OptionalFormMixin


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = ProductSpecifiekInformatie


class ProductUpdateView(OptionalFormMixin, OverheidRoleRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"
    model = ProductSpecifiekInformatie
    form_class = ProductSpecifiekInformatieForm

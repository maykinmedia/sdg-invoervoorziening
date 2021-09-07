from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.forms import ProductSpecifiekInformatieForm
from sdg.producten.models import ProductSpecifiekInformatie


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = ProductSpecifiekInformatie


class ProductUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"
    model = ProductSpecifiekInformatie
    form_class = ProductSpecifiekInformatieForm

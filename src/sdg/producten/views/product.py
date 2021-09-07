from django.views.generic import TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin


class ProductDetailView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "producten/product_detail.html"


class ProductListView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "producten/products.html"

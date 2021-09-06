from django.views.generic import DetailView, FormView, TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.forms import ProductEditForm
from sdg.producten.models import ProductSpecifiekInformatie


class ProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "organisaties/overheid_detail.html"
    model = ProductSpecifiekInformatie


# TODO [US-02] (Lokatie)
class ContactEditView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "organisaties/overheid_update.html"


class ProductListView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "producten/products.html"

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ProductEditView(OverheidRoleRequiredMixin, FormView):
    template_name = "producten/product-edit.html"
    form_class = ProductEditForm

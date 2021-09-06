from django.views.generic import FormView, TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin

from .forms import ProductEditForm


class ProductListView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "products/products.html"

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ProductDetailView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "products/product.html"


class ProductEditView(OverheidRoleRequiredMixin, FormView):
    template_name = "pages/product-edit.html"
    form_class = ProductEditForm


class ContactEditView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "pages/edit-contact.html"

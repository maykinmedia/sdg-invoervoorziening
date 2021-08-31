from django.views.generic import TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin


class ProductListView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "products/products.html"

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ProductDetailView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "products/product.html"


class ContactEditView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "products/edit-contact.html"

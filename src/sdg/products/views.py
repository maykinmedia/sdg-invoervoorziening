from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = "products/products.html"

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ProductDetailView(LoginRequiredMixin, TemplateView):
    template_name = "products/product.html"


class ContactEditView(LoginRequiredMixin, TemplateView):
    template_name = "products/edit-contact.html"

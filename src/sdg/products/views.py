from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = "products/products.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class ProductDetailView(LoginRequiredMixin, TemplateView):
    template_name = "products/product.html"


class ContactEditView(LoginRequiredMixin, TemplateView):
    template_name = "products/edit-contact.html"

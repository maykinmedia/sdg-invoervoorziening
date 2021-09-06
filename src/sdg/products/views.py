from django.views.generic import FormView, TemplateView

from .forms import ProductEditForm


class ProductListView(TemplateView):
    template_name = "pages/products.html"


class ProductDetailView(TemplateView):
    template_name = "pages/product.html"


class ProductEditView(FormView):
    template_name = "pages/product-edit.html"
    form_class = ProductEditForm


class ContactEditView(TemplateView):
    template_name = "pages/edit-contact.html"

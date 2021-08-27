from django.views.generic import TemplateView


class ProductListView(TemplateView):
    template_name = "pages/products.html"


class ProductDetailView(TemplateView):
    template_name = "pages/product.html"


class ContactEditView(TemplateView):
    template_name = "pages/edit-contact.html"

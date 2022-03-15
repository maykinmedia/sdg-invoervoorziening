from django.conf.urls import url

from sdg.producten.views.product import ProductPreviewView, ProductUpdateView

app_name = "producten"
urlpatterns = [
    url(r"(?P<product_pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    url(r"(?P<product_pk>\d+)/preview/$", ProductPreviewView.as_view(), name="preview"),
]

from django.urls import re_path

from sdg.producten.views.product import ProductPreviewView, ProductUpdateView

app_name = "producten"
urlpatterns = [
    re_path(r"(?P<product_pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    re_path(
        r"(?P<product_pk>\d+)/preview/$", ProductPreviewView.as_view(), name="preview"
    ),
]

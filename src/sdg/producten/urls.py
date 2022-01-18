from django.conf.urls import url

from sdg.producten.views.product import (
    ProductCreateRedirectView,
    ProductDetailView,
    ProductPreviewView,
    ProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"r/(?P<product_pk>\d+)/$", ProductCreateRedirectView.as_view(), name="redirect"
    ),
    url(r"(?P<product_pk>\d+)/$", ProductDetailView.as_view(), name="detail"),
    url(r"(?P<product_pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    url(r"(?P<product_pk>\d+)/preview/$", ProductPreviewView.as_view(), name="preview"),
]

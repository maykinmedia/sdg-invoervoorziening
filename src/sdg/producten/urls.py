from django.conf.urls import url

from sdg.producten.views.product import ProductDetailView, ProductUpdateView
from sdg.producten.views.standaard import (
    StandaardProductDetailView,
    StandaardProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>[\d]+)/$",
        ProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>[\d]+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    # Standaard
    url(
        r"^std/(?P<pk>[\d]+)/$",
        StandaardProductDetailView.as_view(),
        name="std_detail",
    ),
    url(
        r"^std/(?P<pk>[\d]+)/edit/$",
        StandaardProductUpdateView.as_view(),
        name="std_edit",
    ),
]

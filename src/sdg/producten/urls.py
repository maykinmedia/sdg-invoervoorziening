from django.conf.urls import url
from django.urls import path

from sdg.producten.views.product import (
    ContactEditView,
    ProductDetailView,
    ProductEditView,
    ProductListView,
)
from sdg.producten.views.standaard import StandaardProductDetailView

app_name = "producten"
urlpatterns = [
    # Standaard
    url(
        r"^standaard/(?P<pk>[\d]+)/$",
        StandaardProductDetailView.as_view(),
        name="standaard_detail",
    ),
    path("", ProductListView.as_view(), name="list"),
    path("detail/1/", ProductDetailView.as_view(), name="detail"),
    path("edit/1/", ProductEditView.as_view(), name="edit"),
    path("edit/contact/", ContactEditView.as_view(), name="edit-contact"),
]

from django.conf.urls import url

from sdg.producten.views.product import ProductDetailView, ProductUpdateView
from sdg.producten.views.referentie import (
    ReferentieProductDetailView,
    ReferentieProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>\d+)/$",
        ProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    # Referentie
    url(
        r"^r/(?P<pk>\d+)/$",
        ReferentieProductDetailView.as_view(),
        name="ref_detail",
    ),
    url(
        r"^r/(?P<pk>\d+)/edit/$",
        ReferentieProductUpdateView.as_view(),
        name="ref_edit",
    ),
]

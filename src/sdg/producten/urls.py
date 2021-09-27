from django.conf.urls import url

from sdg.producten.views.product import (
    ProductCreateRedirectView,
    ProductDetailView,
    ProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>\d+)/$",
        ProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
    url(
        r"^r/(?P<pk>\d+)/(?:(?P<catalog_pk>\d+)/)?$",
        ProductCreateRedirectView.as_view(),
        name="redirect",
    ),
]

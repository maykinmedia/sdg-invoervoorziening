from django.conf.urls import url

from sdg.producten.views.referentie import (
    ReferentieProductDetailView,
    ReferentieProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>[\d]+)/$",
        ReferentieProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>[\d]+)/edit/$", ReferentieProductUpdateView.as_view(), name="edit"),
]

from django.conf.urls import url

from sdg.producten.views.standaard import (
    StandaardProductDetailView,
    StandaardProductUpdateView,
)

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>[\d]+)/$",
        StandaardProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>[\d]+)/edit/$", StandaardProductUpdateView.as_view(), name="edit"),
]

from django.conf.urls import url

from sdg.producten.views.standaard import StandaardProductDetailView

app_name = "producten"
urlpatterns = [
    # Standaard
    url(
        r"^standaard/(?P<pk>[\d]+)/$",
        StandaardProductDetailView.as_view(),
        name="standaard_detail",
    ),
]

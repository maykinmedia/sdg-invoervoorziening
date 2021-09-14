from django.conf.urls import url

from .views import LokaleOverheidDetailView, LokaleOverheidUpdateView

app_name = "organisaties"
urlpatterns = [
    # Organisaties
    #
    # Lokaties
    # TODO [US-02]
    # url(
    #     r"^lokatie/(?P<pk>[\d]+)/$",
    #     LokatieUpdateView.as_view(),
    #     name="lokatie_edit"
    # ),
    # Overheid
    url(
        r"^overheid/(?P<pk>[\d]+)/$",
        LokaleOverheidDetailView.as_view(),
        name="overheid_detail",
    ),
    url(
        r"^overheid/(?P<pk>[\d]+)/edit/$",
        LokaleOverheidUpdateView.as_view(),
        name="overheid_edit",
    ),
]

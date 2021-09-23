from django.conf.urls import url

from .views import LokaleOverheidDetailView, LokaleOverheidUpdateView

app_name = "organisaties"
urlpatterns = [
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

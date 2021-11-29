from django.conf.urls import url
from django.urls import include, path

app_name = "organisaties"
urlpatterns = [
    path("", include("sdg.organisaties.urls.overheid")),
    url(
        r"^(?P<pk>[\d]+)/catalogs/",
        include("sdg.organisaties.urls.catalog", namespace="catalogi"),
    ),
    url(
        r"^(?P<pk>[\d]+)/roles/",
        include("sdg.organisaties.urls.roles", namespace="roles"),
    ),
]

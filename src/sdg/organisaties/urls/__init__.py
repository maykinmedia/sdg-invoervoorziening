from django.urls import include, path, re_path

app_name = "organisaties"
urlpatterns = [
    path("", include("sdg.organisaties.urls.overheid")),
    re_path(
        r"^(?P<pk>[\d]+)/notificaties/",
        include("sdg.organisaties.urls.notificaties", namespace="notificaties"),
    ),
    re_path(
        r"^(?P<pk>[\d]+)/productenlijst/",
        include("sdg.organisaties.urls.catalog", namespace="productenlijst"),
    ),
    re_path(
        r"^(?P<pk>[\d]+)/roles/",
        include("sdg.organisaties.urls.roles", namespace="roles"),
    ),
]

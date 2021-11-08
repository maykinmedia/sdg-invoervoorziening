from django.conf.urls import include, url
from django.urls import path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                url(
                    r"schema/openapi\.(?:yaml|yml)",
                    SpectacularYAMLAPIView.as_view(),
                    name="schema",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(url_name="schema"),
                    name="schema-redoc",
                ),
            ]
        ),
    ),
    path(
        "v1/",
        SpectacularJSONAPIView.as_view(),
        name="schema-json",
    ),
]

from django.conf.urls import include, url
from django.urls import path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from rest_framework import routers

from sdg.api.views import (
    CatalogusViewSet,
    LokaleOverheidViewSet,
    LokatieViewSet,
    ProductViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register("catalogi", CatalogusViewSet)
router.register("producten", ProductViewSet)
router.register("organisaties", LokaleOverheidViewSet)
router.register("locaties", LokatieViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                path(
                    "schema/openapi.yaml",
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

from django.urls import include, path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from vng_api_common import routers

from sdg.api.views import (
    CatalogusViewSet,
    LocatieViewSet,
    LokaleOverheidViewSet,
    ProductConceptViewSet,
    ProductHistoryViewSet,
    ProductViewSet,
)

app_name = "api"

router = routers.DefaultRouter(trailing_slash=False)
router.register("catalogi", CatalogusViewSet)
router.register(
    "producten",
    ProductViewSet,
    [
        routers.nested(
            "historie",
            ProductHistoryViewSet,
            basename="product-history",
        ),
        routers.nested(
            "concept",
            ProductConceptViewSet,
            basename="product-concept",
        ),
    ],
)
router.register("organisaties", LokaleOverheidViewSet)
router.register("locaties", LocatieViewSet, basename="locatie")

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                path(
                    "openapi.yaml",
                    SpectacularYAMLAPIView.as_view(),
                    name="schema-yaml",
                ),
                path(
                    "openapi.json",
                    SpectacularJSONAPIView.as_view(),
                    name="schema-json",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(url_name="api:schema-yaml"),
                    name="schema",
                ),
            ]
        ),
    ),
]

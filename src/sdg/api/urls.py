from django.urls import include, path
from django.views.generic.base import TemplateView

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from rest_framework.settings import api_settings
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
    path(
        "",
        TemplateView.as_view(
            template_name="api/index.html",
            extra_context={"version": api_settings.DEFAULT_VERSION},
        ),
    ),
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

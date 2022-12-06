from django.db.models import Prefetch

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from sdg.api.filters import ProductenCatalogusFilterSet
from sdg.api.serializers import ProductenCatalogusSerializer
from sdg.core.models import ProductenCatalogus
from sdg.producten.models import Product


@extend_schema_view(
    list=extend_schema(
        description="Een lijst van alle catalogi.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="organisatie",
                description="De UUID van een organisatie om aan te geven van welke organisatie u de catalogi wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="De OWMS Identifier  van een organisatie om aan te geven van welke organisatie u de catalogi wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Het OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de catalogi wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Het paginanummer binnen de lijst van resultaten.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Een catalogus behoort aan een organisatie en is een verzameling van producten.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="De UUID van een catalogus.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
)
class CatalogusViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by UUID"""

    serializer_class = ProductenCatalogusSerializer
    filterset_class = ProductenCatalogusFilterSet
    lookup_field = "uuid"
    queryset = (
        ProductenCatalogus.objects.active_organization()
        .select_related(
            "lokale_overheid",
        )
        .prefetch_related(
            Prefetch(
                "producten",
                queryset=Product.objects.select_related("generiek_product__upn"),
            )
        )
    )

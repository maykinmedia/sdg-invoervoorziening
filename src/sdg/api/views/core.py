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
        description="Een lijst van alle categorieën die gebruikt worden door organisaties.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="organisatie",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de catalogus wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="Hierin vermeld u de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier)  van een organisatie om aan te geven van welke organisatie u de catalogus wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Hierin vermeld u de OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de catalogus wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Hierin kunt u aangeven welke pagina (https://en.wikipedia.org/wiki/Pagination) u wilt zien.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Catalogus die wordt gebruikt door een organisatie.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de catalogus wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
)
class CatalogusViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by uuid"""

    serializer_class = ProductenCatalogusSerializer
    filterset_class = ProductenCatalogusFilterSet
    lookup_field = "uuid"
    queryset = ProductenCatalogus.objects.select_related(
        "lokale_overheid",
    ).prefetch_related(
        Prefetch(
            "producten",
            queryset=Product.objects.select_related("generiek_product__upn"),
        )
    )

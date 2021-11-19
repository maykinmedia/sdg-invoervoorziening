from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from sdg.api.filters import ProductenCatalogusFilterSet
from sdg.api.serializers import ProductenCatalogusSerializer
from sdg.core.models import ProductenCatalogus


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle catalogi die worden gebruikt door organisaties."
    ),
    retrieve=extend_schema(
        description="Catalogus die wordt gebruikt door een organisatie."
    ),
)
class CatalogusViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by uuid"""

    serializer_class = ProductenCatalogusSerializer
    filterset_class = ProductenCatalogusFilterSet
    lookup_field = "uuid"
    queryset = ProductenCatalogus.objects.all()

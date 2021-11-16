from rest_framework import viewsets

from sdg.api.filters import ProductenCatalogusFilterSet
from sdg.api.serializers import ProductenCatalogusSerializer
from sdg.core.models import ProductenCatalogus


class CatalogusViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by uuid"""

    serializer_class = ProductenCatalogusSerializer
    filterset_class = ProductenCatalogusFilterSet
    lookup_field = "uuid"
    queryset = ProductenCatalogus.objects.all()

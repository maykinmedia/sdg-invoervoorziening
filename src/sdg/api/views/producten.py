from rest_framework import viewsets

from sdg.api.filters import ProductFilterSet
from sdg.api.mixins import MultipleSerializerMixin
from sdg.api.serializers import ProductListSerializer, ProductSerializer
from sdg.producten.models import Product


class ProductViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = Product.objects.all()
    filterset_class = ProductFilterSet
    serializer_classes = {
        "retrieve": ProductSerializer,
        "list": ProductListSerializer,
    }

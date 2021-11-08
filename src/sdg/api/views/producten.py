from rest_framework import viewsets

from sdg.api.mixins import MultipleSerializerMixin
from sdg.api.serializers import ProductListSerializer, ProductSerializer
from sdg.producten.models import Product


class ProductViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality catalog, retrieved by uuid"""

    serializer_class = ProductSerializer
    lookup_field = "uuid"
    queryset = Product.objects.all()
    serializer_classes = {
        "retrieve": ProductSerializer,
        "list": ProductListSerializer,
    }

from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from sdg.api.filters import ProductFilterSet
from sdg.api.serializers import ProductSerializer, ProductVersieSerializer
from sdg.producten.models import Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a product, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = Product.objects.all()
    filterset_class = ProductFilterSet
    serializer_class = ProductSerializer


class ProductHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the version history of a product."""

    lookup_field = "uuid"
    serializer_class = ProductVersieSerializer

    def get_queryset(self):
        product = Product.objects.get(uuid=self.kwargs["product_uuid"])
        return product.get_latest_versions(exclude_concept=True)

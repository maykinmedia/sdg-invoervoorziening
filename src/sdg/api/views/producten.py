from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sdg.api.filters import ProductFilterSet
from sdg.api.mixins import MultipleSerializerMixin
from sdg.api.serializers import (
    LocalizedProductSerializer,
    ProductListSerializer,
    ProductSerializer,
    ProductVersieSerializer,
)
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

    @extend_schema(
        description="Retrieve the version history of a product.",
        responses={"200": ProductVersieSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="historie",
        methods=["get"],
        serializer_class=ProductVersieSerializer,
    )
    def history(self, request, uuid=None):
        """Retrieve the version history of a product."""
        product_versions = self.get_object().get_latest_versions(exclude_concept=True)
        serializer = self.get_serializer(product_versions, many=True)
        return Response(serializer.data)

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from sdg.api.filters import ProductFilterSet
from sdg.api.serializers import ProductSerializer, ProductVersieSerializer
from sdg.producten.models import Product, ProductVersie


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle producten die voorkomen in alle catalogi."
    ),
    retrieve=extend_schema(description="Product dat voorkomt in een catalogus."),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a product, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = (
        Product.objects.select_related(
            "catalogus",
            "catalogus__lokale_overheid",
            "generiek_product",
            "generiek_product__upn",
        )
        .prefetch_related(
            "gerelateerde_producten",
            "lokaties",
        )
        .active()
        .order_by("generiek_product__upn__upn_label")
    )
    filterset_class = ProductFilterSet
    serializer_class = ProductSerializer


@extend_schema_view(
    list=extend_schema(description="Lijst van alle productversies van een product."),
)
class ProductHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the version history of a product."""

    lookup_field = "uuid"
    queryset = ProductVersie.objects.all()
    serializer_class = ProductVersieSerializer

    def get_queryset(self):
        product = Product.objects.get(uuid=self.kwargs["product_uuid"])
        return product.get_latest_versions(exclude_concept=True)

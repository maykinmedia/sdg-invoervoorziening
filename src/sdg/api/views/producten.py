from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from sdg.api.filters import ProductFilterSet
from sdg.api.permissions import Permissions
from sdg.api.serializers import ProductSerializer, ProductVersieSerializer
from sdg.core.models.logius import Overheidsorganisatie
from sdg.producten.models import Product, ProductVersie


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle producten die voorkomen in alle catalogi."
    ),
    retrieve=extend_schema(description="Product dat voorkomt in een catalogus."),
    create=extend_schema(
        description="Maak een nieuwe product versie aan of update een concept voor een catalogus."
    ),
)
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
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
            "locaties",
            "versies",
            "versies__vertalingen",
        )
        .active()
        .order_by("generiek_product__upn__upn_label")
    )
    filterset_class = ProductFilterSet
    serializer_class = ProductSerializer
    permission_classes = [Permissions]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            organisatie = view.request.data.get("verantwoordelijke_organisatie", None)
            if not organisatie:
                return None

            for field in ["owms_pref_label", "owms_identifier"]:
                if field in organisatie:
                    try:
                        return Overheidsorganisatie.objects.get(
                            **{field: organisatie.get(field)}
                        )
                    except Overheidsorganisatie.DoesNotExist:
                        return None

        return None


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID van het product waarvoor de versies worden opgevraagd.",
            ),
        ],
        description="Lijst van alle productversies van een product.",
    ),
)
class ProductHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the version history of a product."""

    serializer_class = ProductVersieSerializer
    queryset = ProductVersie.objects.none()

    def get_queryset(self):
        return (
            ProductVersie.objects.published()
            .filter(product__uuid=self.kwargs["product_uuid"])
            .prefetch_related("vertalingen")
        )


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID van het product waarvoor de versie is opgevraagd.",
            ),
        ],
        description="Lijst van concept-productversies voor dit product.",
    ),
)
class ProductConceptViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the concept version of a product."""

    serializer_class = ProductVersieSerializer
    queryset = ProductVersie.objects.none()

    def get_queryset(self):
        return (
            ProductVersie.objects.filter(publicatie_datum=None)
            .filter(product__uuid=self.kwargs["product_uuid"])
            .prefetch_related("vertalingen")
        )

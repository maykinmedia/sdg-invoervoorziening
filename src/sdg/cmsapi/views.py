from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view

from sdg.cmsapi.serializers import (
    LocalizedGenericProductSerializer,
)
from sdg.producten.models.localized import LocalizedProduct, LocalizedGeneriekProduct


@extend_schema_view(
    retrieve=extend_schema(description="Generiek product"),
)
class ProductTranslation(viewsets.ReadOnlyModelViewSet):
    queryset = LocalizedProduct.objects.none()
    serializer_class = LocalizedGenericProductSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwargs = ["product_id", "taal"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        language = self.request.query_params.get("taal", None)

        localized_products = (
            LocalizedProduct.objects.filter(
                product_versie__product__id=product_id,
                taal="nl",
            )
            .order_by("product_versie")
            .first()
        )
        if localized_products:
            if language:
                return LocalizedGeneriekProduct.objects.filter(
                    generiek_product=localized_products.product_versie.product.referentie_product.generiek_product,
                    taal=language,
                )
            return LocalizedGeneriekProduct.objects.filter(
                generiek_product=localized_products.product_versie.product.referentie_product.generiek_product,
            )
        return []

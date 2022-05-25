from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from sdg.cmsapi.serializers import LocalizedGenericProductSerializer
from sdg.producten.models import Product


class ProductTranslation(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.none()
    serializer_class = LocalizedGenericProductSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwargs = ["product_id", "taal"]
    schema = None

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        language = self.request.query_params.get("taal", None)

        if product_id:
            product = Product.objects.filter(pk=product_id).first()
            if product:
                if language:
                    return product.generiek_product.vertalingen.filter(taal=language)
                else:
                    return product.generiek_product.vertalingen.order_by("-taal")

        return []

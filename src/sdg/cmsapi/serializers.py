from rest_framework import serializers
from sdg.producten.models.localized import LocalizedGeneriekProduct


class LocalizedGenericProductSerializer(serializers.ModelSerializer):
    generiek_product = serializers.CharField(read_only=True)
    product_titel = serializers.CharField(read_only=True)

    class Meta:
        model = LocalizedGeneriekProduct
        fields = (
            "taal",
            "generiek_product",
            "product_titel",
        )

from rest_framework import serializers

from sdg.core.models import ProductenCatalogus


class ProductenCatalogusSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for ProductenCatalogus details, including organizations and products."""

    class Meta:
        model = ProductenCatalogus
        fields = (
            "uuid",
            "domein",
            "naam",
            "lokale_overheid",
            "is_referentie_catalogus",
            "referentie_catalogus",
            "toelichting",
            "versie",
        )
        extra_kwargs = {
            "lokale_overheid": {
                "lookup_field": "uuid",
                "view_name": "lokaleoverheid-detail",
            },
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "productencatalogus-detail",
            },
        }

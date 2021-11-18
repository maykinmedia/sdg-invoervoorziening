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
            "is_referentie_catalogus",
            "referentie_catalogus",
            "toelichting",
            "versie",
            "producten",
        )
        extra_kwargs = {
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "productencatalogus-detail",
            },
            "producten": {"lookup_field": "uuid", "view_name": "product-detail"},
        }
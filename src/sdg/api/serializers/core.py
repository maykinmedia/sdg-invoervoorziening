from rest_framework import serializers

from sdg.api.serializers.organisaties import OrganisatieBaseSerializer
from sdg.api.serializers.producten import ProductBaseSerializer
from sdg.core.models import ProductenCatalogus


class ProductenCatalogusSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for ProductenCatalogus details, including organizations and products."""

    organisatie = OrganisatieBaseSerializer(source="lokale_overheid")
    producten = ProductBaseSerializer(many=True)

    class Meta:
        model = ProductenCatalogus
        fields = (
            "url",
            "uuid",
            "domein",
            "naam",
            "organisatie",
            "is_referentie_catalogus",
            "referentie_catalogus",
            "toelichting",
            "versie",
            "producten",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:productencatalogus-detail",
                "lookup_field": "uuid",
            },
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
            },
        }

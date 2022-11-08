from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from sdg.api.serializers.organisaties import LokaleOverheidBaseSerializer
from sdg.api.serializers.producten import ProductBaseSerializer
from sdg.core.models import ProductenCatalogus


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Organisaties/put",
            value={
                "url": "http://example.com/api/v1/catalogi/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "uuid": "095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "domein": "SDG",
                "naam": "Naam (SDG Catalogus)",
                "organisatie": {
                    "url": "http://example.com/api/v1/organisaties/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                    "owmsIdentifier": "http://standaarden.overheid.nl/owms/terms/product",
                    "owmsPrefLabel": "Organisatie naam",
                    "owmsEndDate": "2023-01-01T00:01:22Z",
                },
                "isReferentieCatalogus": False,
                "referentieCatalogus": "http://example.com/api/v1/catalogi/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "toelichting": "Een stuk tekst die toelichting geeft over de catalogus",
                "versie": 1,
                "producten": [
                    {
                        "url": "http://example.com/api/v1/producten/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                        "upnUri": "http://standaarden.overheid.nl/owms/terms/product",
                        "upnLabel": "Naam van het product",
                    }
                ],
            },
        ),
    ]
)
class ProductenCatalogusSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for ProductenCatalogus details, including organizations and products."""

    organisatie = LokaleOverheidBaseSerializer(
        source="lokale_overheid", help_text="De organisatie die deze catalogus beheert."
    )
    producten = ProductBaseSerializer(
        many=True,
        help_text="Alle producten binnen deze catalogus.",
    )

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
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
            "uuid": {"help_text": "De UUID van de specifieke catalogus"},
            "domein": {
                "help_text": "Een afkorting die wordt gebruikt om het domein aan te duiden."
            },
            "naam": {"help_text": "De naam van de catalogus"},
            "is_referentie_catalogus": {
                "help_text": "Een boolean die aangeeft of de catalogus een referentie catalogus betreft. Een referentie catalogus bevat geen echte productbeschrijvingen."
            },
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "De URL van de referentieproductcatalogus waar deze productcatalogus aan gekoppeld is",
            },
            "toelichting": {
                "help_text": "Hierin staat de beschreven waar deze catalogus voor dient."
            },
            "versie": {
                "help_text": "De versie van deze catalogus. Op dit moment heeft de waarde geen betekenis."
            },
        }

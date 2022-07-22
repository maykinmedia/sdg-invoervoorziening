from rest_framework import serializers

from sdg.api.serializers.organisaties import LokaleOverheidBaseSerializer
from sdg.api.serializers.producten import ProductBaseSerializer
from sdg.core.models import ProductenCatalogus


class ProductenCatalogusSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for ProductenCatalogus details, including organizations and products."""

    organisatie = LokaleOverheidBaseSerializer(source="lokale_overheid")
    producten = ProductBaseSerializer(
        many=True,
        help_text="""Het product waar dit product van af hankelijk is dit geven we aan met een van de volgende velden:
        - Fields: `url`, `upnUri`, `upnLabel`
        """,
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
                "help_text": "De url van de specifieke catalogi api call",
            },
            "uuid": {
                "help_text": "De UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van de specifieke catalogi"
            },
            "domein": {
                "help_text": "Een afkorting die wordt gebruikt om het domein aan te duiden."
            },
            "naam": {"help_text": "De naam van de catalogi"},
            "is_referentie_catalogus": {
                "help_text": "Dit is een boolean die aangeeft of de catalogus een referentie catalogus is, als deze op false staat dan is het een producten catalogus."
            },
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "Dit is de api call url van de referentie catalogus waar dit product aan gekoppeld is.",
            },
            "toelichting": {
                "help_text": "Hierin staat de toelichting beschreven waarom deze catalogi bestaat."
            },
            "versie": {
                "help_text": "Dit is de versie van deze catalogi, hierdoor kunt u zien of er wijzigingen zijn aangebracht voor de catalogi."
            },
        }

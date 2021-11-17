from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sdg.api.serializers.logius import OverheidsorganisatieSerializer
from sdg.organisaties.models import LokaleOverheid, Lokatie


class OpeningstijdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lokatie
        fields = (
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        )


class LokatieSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for location details, including contact details, address and opening times."""

    openingstijden = SerializerMethodField(method_name="get_openingstijden")

    class Meta:
        model = Lokatie
        fields = (
            "uuid",
            "land",
            "naam",
            "nummer",
            "plaats",
            "postcode",
            "straat",
            "openingstijden",
        )

    def get_openingstijden(self, obj: Lokatie) -> OpeningstijdenSerializer:
        return OpeningstijdenSerializer(obj).data


class LokaleOverheidSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for municipality details, including organization details, catalogs and locations."""

    organisatie = OverheidsorganisatieSerializer()

    bevoegde_organisatie = OverheidsorganisatieSerializer()
    ondersteunings_organisatie = OverheidsorganisatieSerializer()
    verantwoordelijke_organisatie = OverheidsorganisatieSerializer()

    class Meta:
        model = LokaleOverheid
        fields = (
            "uuid",
            "organisatie",
            "lokaties",
            "catalogi",
            "contact_naam",
            "contact_website",
            "contact_emailadres",
            "contact_telefoonnummer",
            "bevoegde_organisatie",
            "ondersteunings_organisatie",
            "verantwoordelijke_organisatie",
        )
        extra_kwargs = {
            "catalogi": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
            },
            "lokaties": {
                "lookup_field": "uuid",
                "view_name": "api:lokatie-detail",
            },
        }

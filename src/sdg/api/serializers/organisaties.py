from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedRelatedField

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
    organisatie = HyperlinkedRelatedField(
        source="lokale_overheid",
        lookup_field="uuid",
        view_name="api:lokaleoverheid-detail",
        queryset=LokaleOverheid.objects.all(),
    )

    class Meta:
        model = Lokatie
        fields = (
            "url",
            "uuid",
            "naam",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "openingstijden",
            "organisatie",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:lokatie-detail",
                "lookup_field": "uuid",
            },
        }

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
            "url",
            "uuid",
            "organisatie",
            "locaties",
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
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
            },
            "catalogi": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
            },
            "locaties": {
                "source": "lokaties",
                "lookup_field": "uuid",
                "view_name": "api:lokatie-detail",
            },
        }

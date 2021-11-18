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

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="OWMS identifier van de hoofdorganisatie van deze lokale overheid.",
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="OWMS einddatum van de hoofdorganisatie van deze lokale overheid.",
    )

    bevoegde_organisatie = OverheidsorganisatieSerializer()
    ondersteunings_organisatie = OverheidsorganisatieSerializer()
    verantwoordelijke_organisatie = OverheidsorganisatieSerializer()

    class Meta:
        model = LokaleOverheid
        fields = (
            "url",
            "uuid",
            "owms_identifier",
            "owms_pref_label",
            "owms_end_date",
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

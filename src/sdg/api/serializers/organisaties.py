from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sdg.api.serializers.logius import OverheidsorganisatieSerializer
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


class OpeningstijdenSerializer(serializers.ModelSerializer):
    """Serializer for location based opening times."""

    class Meta:
        model = Locatie
        fields = (
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        )


class OrganisatieBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer that exposes a small subset of the fields for a Organisatie, used in references to a organisation.
    - Fields: `url`, `owmsIdentifier`, `owmsPrefLabel`
    """

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="OWMS identifier van de hoofdorganisatie van deze lokale overheid.",
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
    )

    class Meta:
        model = LokaleOverheid
        fields = ("url", "owms_identifier", "owms_pref_label")
        extra_kwargs = {
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
            },
        }


class LocatieSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for location details, including contact details, address and opening times."""

    openingstijden = SerializerMethodField(method_name="get_openingstijden")
    organisatie = OrganisatieBaseSerializer(source="lokale_overheid")

    class Meta:
        model = Locatie
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
            "openingstijden_opmerking",
            "organisatie",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:locatie-detail",
                "lookup_field": "uuid",
            },
        }

    def get_openingstijden(self, obj: Locatie) -> OpeningstijdenSerializer:
        return OpeningstijdenSerializer(obj).data


class LokaleOverheidSerializer(OrganisatieBaseSerializer):
    """Serializer for municipality details, including organization details, catalogs and locations."""

    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="OWMS einddatum van de hoofdorganisatie van deze lokale overheid.",
    )

    bevoegde_organisatie = OverheidsorganisatieSerializer()
    ondersteunings_organisatie = OverheidsorganisatieSerializer()
    verantwoordelijke_organisatie = OverheidsorganisatieSerializer()
    locaties = LocatieSerializer(many=True)

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
                "help_text": "Lijst van catalogi die deze organisatie gebruikt.",
            },
        }

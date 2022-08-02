from django.db import transaction
from django.http import Http404

from rest_framework import serializers

from sdg.api.serializers.logius import OverheidsorganisatieSerializer
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)


class OpeningstijdenSerializer(serializers.ModelSerializer):
    """Een lijst met de openings tijden van maandag tot zondag van deze locatie."""

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
        extra_kwargs = {
            "maandag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan door middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "dinsdag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "woensdag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "donderdag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "vrijdag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "zaterdag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
            "zondag": {
                "help_text": """De openingstijden van maandag. Deze openingstijden geven
                we aan ter middel van een lijst met daarin de openingstijden zoals hier: `[“9:00 - 18:00”]`"""
            },
        }


class BevoegdeOrganisatieSerializer(serializers.ModelSerializer):
    """De ondersteunende organisaties (standaard heeft een organisatie altijd zichzelf als een bevoegde organisatie.)"""

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="Dit is de de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier) van een de bevoegde organisatie.",
        default=None,
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="Dit is de de OWMS Prefered Label van een de bevoegde organisatie.",
        default=None,
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="Dit is de eind datum van de bevoegde organisatie, als deze null is betekend dat de bevoegde organisatie nog bestaat.",
        default=None,
        required=False,
        read_only=True,
    )
    naam = serializers.CharField(
        help_text="De naam van de bevoegde organisatie. Deze mag alleen afwijken indien er geen bekende overheidsorganisatie is.",
        read_only=True,
    )

    class Meta:
        model = BevoegdeOrganisatie
        fields = (
            "naam",
            "owms_identifier",
            "owms_pref_label",
            "owms_end_date",
        )


class LokaleOverheidBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Organisaties verbonden aan deze locatie, dit geven we aan met een van de volgende velden:
    - Fields: `url`, `owmsIdentifier`, `owmsPrefLabel`
    """

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="""Dit is de de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier)
        van een de organisatie die gekoppeld is aan deze locatie.
        """,
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="Dit is de de OWMS Prefered Label van de organisatie die gekoppeld is aan deze locatie.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="Dit is de eind datum van de organisatie, als deze null is betekend dat de organisatie actief is.",
        read_only=True,
        required=False,
    )

    class Meta:
        model = LokaleOverheid
        fields = ("url", "owms_identifier", "owms_pref_label", "owms_end_date")
        extra_kwargs = {
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
                "help_text": "De Url van de api call voor het inzien van de data van het specifieke product.",
            },
        }


class LocatieBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Een lijst met alle locaties die gekoppeld zijn aan deze organisatie."""

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
            "openingstijden_opmerking",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:locatie-detail",
                "lookup_field": "uuid",
                "help_text": "De URL van een specifieke organisatie, wordt tevens gebruikt om met andere aanroepen te refereren aan 1 organisatie",
            },
            "naam": {"required": False, "help_text": "De naam van de locatie."},
            "uuid": {
                "required": False,
                "help_text": "De uuid van een specifieke organisatie (https://en.wikipedia.org/wiki/Universally_unique_identifier).",
            },
            "straat": {"help_text": "De straatnaam van de locatie."},
            "nummer": {"help_text": "Het huisnummer van de locatie."},
            "postcode": {"help_text": "De postcode van de locatie."},
            "plaats": {"help_text": "De plaatsnaam van de locatie."},
            "land": {"help_text": "Het land waar van de locatie."},
            "openingstijden_opmerking": {
                "help_text": """Een opmerking over de openingstijden, hier kunt u extra informatie
                kwijt over de openingstijden wanneer dit gewenst is."""
            },
        }


class LocatieSerializer(LocatieBaseSerializer):
    """Serializer for location details, including contact details, address and opening times."""

    organisatie = LokaleOverheidBaseSerializer(source="lokale_overheid", required=False)
    openingstijden = OpeningstijdenSerializer(source="*")

    class Meta(LocatieBaseSerializer.Meta):
        fields = LocatieBaseSerializer.Meta.fields + (
            "organisatie",
            "openingstijden",
        )

    def validate(self, attrs):
        if self.context["request"].method == "POST":
            lokale_overheid = attrs.get("lokale_overheid", None)

            if not lokale_overheid:
                raise serializers.ValidationError(
                    "You forgot to provide the owms_pref_label and∕or the owms_identifier"
                )

            if "organisatie" not in lokale_overheid:
                raise serializers.ValidationError(
                    "You forgot to provide the owms_pref_label and∕or the owms_identifier"
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lokale_overheid = validated_data.pop("lokale_overheid", None)
        initial_organisatie = lokale_overheid["organisatie"]

        try:
            if "owms_pref_label" in initial_organisatie:
                validated_data["lokale_overheid"] = LokaleOverheid.objects.get(
                    organisatie__owms_pref_label=initial_organisatie["owms_pref_label"]
                )
        except LokaleOverheid.DoesNotExist:
            raise serializers.ValidationError("Received a non existing owms_pref_label")

        try:
            if (
                "lokale_overheid" not in validated_data
                and "owms_identifier" in initial_organisatie
            ):
                validated_data["lokale_overheid"] = LokaleOverheid.objects.get(
                    organisatie__owms_identifier=initial_organisatie["owms_identifier"]
                )
        except LokaleOverheid.DoesNotExist:
            raise serializers.ValidationError("Received a non existing owms_identifier")

        record = super().create(validated_data)

        return record

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop("lokale_overheid", None)

        validated_data["lokale_overheid"] = instance.lokale_overheid

        record = super().update(instance, validated_data)

        return record


class LokaleOverheidSerializer(LokaleOverheidBaseSerializer):
    """Serializer for municipality details, including organization details, catalogs and locations."""

    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="Dit is de eind datum van de organisatie, als deze null is betekend dat de organisatie actief is.",
        required=False,
        read_only=True,
    )

    bevoegde_organisaties = BevoegdeOrganisatieSerializer(
        many=True,
        help_text="Organisaties die rechten hebben tot deze organisatie, standaard heeft een organisatie altijd zichzelf als een bevoegde organisatie.",
    )
    ondersteunings_organisatie = OverheidsorganisatieSerializer()
    locaties = LocatieBaseSerializer(
        many=True,
        help_text="Een lijst met alle locaties die gekoppeld zijn aan deze organisatie.",
    )

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
            "contact_website",
            "contact_emailadres",
            "contact_telefoonnummer",
            "contact_formulier_link",
            "bevoegde_organisaties",
            "ondersteunings_organisatie",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
                "help_text": "De URL van een specifieke organisatie, wordt tevens gebruikt om met andere aanroepen te refereren aan 1 oranisatie.",
            },
            "catalogi": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "Lijst van catalogi die deze organisatie gebruikt.",
            },
        }

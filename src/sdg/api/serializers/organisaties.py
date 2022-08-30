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


class BevoegdeOrganisatieSerializer(serializers.ModelSerializer):
    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="OWMS identifier van de hoofdorganisatie van deze lokale overheid.",
        default=None,
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
        default=None,
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De einddatum, zoals gevonden in het OWMS-model.",
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
    """De organisatie die gekoppeld zit aan deze locatie dit geven we aan met een van de volgende velden:
    - Fields: `url`, `owmsIdentifier`, `owmsPrefLabel`
    """

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="OWMS identifier van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De einddatum, zoals gevonden in het OWMS-model.",
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
                "help_text": "De api url voor het zien van de gegevens van deze locatie.",
            },
        }


class LocatieBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer that exposes a subset of the fields for a location, used in references to a location."""

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
            },
            "naam": {
                "required": False,
            },
            "uuid": {
                "required": False,
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
        help_text="OWMS einddatum van de hoofdorganisatie van deze lokale overheid.",
    )

    bevoegde_organisaties = BevoegdeOrganisatieSerializer(many=True)
    ondersteunings_organisatie = OverheidsorganisatieSerializer()
    locaties = LocatieBaseSerializer(many=True)

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
            },
            "catalogi": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "Lijst van catalogi die deze organisatie gebruikt.",
            },
        }

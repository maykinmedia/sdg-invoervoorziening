from django.db import transaction

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)


class OpeningstijdenSerializer(serializers.ModelSerializer):
    """Een lijst met de openings tijden van maandag tot en met zondag van deze locatie."""

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
                "help_text": """De openingstijden op maandag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "dinsdag": {
                "help_text": """De openingstijden op dinsdag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "woensdag": {
                "help_text": """De openingstijden op woensdag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "donderdag": {
                "help_text": """De openingstijden op donderdag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "vrijdag": {
                "help_text": """De openingstijden op vrijdag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "zaterdag": {
                "help_text": """De openingstijden op zaterdag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
            "zondag": {
                "help_text": """De openingstijden op zondag. Tijden dienen als volgt opgegeven te worden: `["9:00 - 18:00"]`"""
            },
        }


class BevoegdeOrganisatieSerializer(serializers.ModelSerializer):
    """De ondersteunende organisaties (standaard heeft een organisatie altijd zichzelf als een bevoegde organisatie.)"""

    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="De OWMS Identifier van een de bevoegde organisatie.",
        default=None,
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="Het OWMS Prefered Label van een de bevoegde organisatie.",
        default=None,
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De eind datum van de bevoegde organisatie. Indien de waarde `null` is, dan is organisatie actief.",
        default=None,
        required=False,
        read_only=True,
    )
    naam = serializers.CharField(
        help_text="De naam van de bevoegde organisatie. Deze mag alleen afwijken indien er geen bekende overheidsorganisatie is.",
        default=None,
        required=False,
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
    owms_identifier = serializers.URLField(
        source="organisatie.owms_identifier",
        help_text="""De OWMS Identifier van een de organisatie die gekoppeld is aan deze locatie.""",
        required=True,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="Het OWMS Prefered Label van de organisatie die gekoppeld is aan deze locatie.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De eind datum van de organisatie. Indien de waarde `null` is, dan is organisatie actief.",
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
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
        }


class LocatieBaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Locatie
        fields = (
            "url",
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
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
            "naam": {"required": False, "help_text": "De naam van de locatie."},
            "straat": {"help_text": "De straatnaam van de locatie."},
            "nummer": {
                "help_text": "Het huisnummer van de locatie, inclusief eventuele toevoegingen."
            },
            "postcode": {"help_text": "De postcode van de locatie."},
            "plaats": {"help_text": "De plaatsnaam van de locatie."},
            "land": {"help_text": "Het land van de locatie."},
            "openingstijden_opmerking": {
                "help_text": """Een opmerking over de openingstijden. Hier kunt u extra informatie
                kwijt over de openingstijden wanneer dit gewenst is."""
            },
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Locaties",
            value={
                "url": "http://example.com/api/v1/locaties/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "naam": "Locatie naam",
                "straat": "Straat naam",
                "nummer": "12",
                "postcode": "1234AA",
                "plaats": "Plaats naam",
                "land": "Nederland",
                "openingstijdenOpmerking": "Informatie over de locatie.",
                "organisatie": {
                    "url": "http://example.com/api/v1/organisaties/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                    "owmsIdentifier": "http://standaarden.overheid.nl/owms/terms/product",
                    "owmsPrefLabel": "Organisatie naam",
                    "owmsEndDate": "2022-01-01T00:01:22Z",
                },
                "openingstijden": {
                    "maandag": ["07:00-18:00"],
                    "dinsdag": ["07:00-18:00"],
                    "woensdag": ["07:00-18:00"],
                    "donderdag": ["07:00-18:00"],
                    "vrijdag": ["07:00-18:00"],
                    "zaterdag": ["09:00-12:00", "13:00-15:00"],
                    "zondag": ["09:00-12:00", "13:00-15:00"],
                },
            },
        ),
    ]
)
class LocatieSerializer(LocatieBaseSerializer):
    organisatie = LokaleOverheidBaseSerializer(
        source="lokale_overheid",
        required=False,
        help_text="Organisatie van deze locatie. Om een locatie aan te maken of bij te werken **MOET** de `url` of `owmsIdentifier` opgegeven worden.",
    )
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
                    {"organisatie": "Het veld 'owmsIdentifier' is verplicht."}
                )

            if "organisatie" not in lokale_overheid:
                raise serializers.ValidationError(
                    {"organisatie": "Het veld 'owmsIdentifier' is verplicht."}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lokale_overheid = validated_data.pop("lokale_overheid", None)
        initial_organisatie = lokale_overheid["organisatie"]

        try:
            validated_data["lokale_overheid"] = LokaleOverheid.objects.get(
                organisatie__owms_identifier=initial_organisatie["owms_identifier"]
            )
        except LokaleOverheid.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "organisatie.owmsIdentifier": "De waarde van het veld 'owmsIdentifier' is ongeldig. Het object met deze waarde bestaat niet."
                }
            )
        except KeyError:
            raise serializers.ValidationError(
                {
                    "organisatie.owmsIdentifier": "Het veld 'owmsIdentifier' is verplicht."
                }
            )

        record = super().create(validated_data)

        return record

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop("lokale_overheid", None)

        validated_data["lokale_overheid"] = instance.lokale_overheid

        record = super().update(instance, validated_data)

        return record


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Organisaties/get",
            value={
                "url": "http://example.com/api/v1/organisaties/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "uuid": "095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "owmsIdentifier": "http://standaarden.overheid.nl/owms/terms/product",
                "owmsPrefLabel": "Organisatie naam",
                "owmsEndDate": "2022-01-01T00:01:22Z",
                "locaties": [
                    {
                        "url": "http://example.com/api/v1/locaties/095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                        "naam": "Locatie naam",
                        "straat": "Straat naam",
                        "nummer": "12",
                        "postcode": "1234AA",
                        "plaats": "Plaats naam",
                        "land": "Nederland",
                        "openingstijdenOpmerking": "Informatie over de locatie.",
                    }
                ],
                "catalogi": [
                    "http://example.com/api/v1/catalogi/095be615-a8ad-4c33-8e9c-c7612fbf6c9f"
                ],
                "contactWebsite": "http://example.com",
                "contactEmailadres": "user@example.com",
                "contactTelefoonnummer": "31021234567",
                "contactFormulierLink": "http://example.com",
                "bevoegdeOrganisaties": [
                    {
                        "naam": "Organisatie naam",
                        "owmsIdentifier": "http://standaarden.overheid.nl/owms/terms/product",
                        "owmsPrefLabel": "Organisatie naam",
                        "owmsEndDate": "2022-01-01T00:01:22Z",
                    }
                ],
            },
        ),
    ]
)
class LokaleOverheidSerializer(LokaleOverheidBaseSerializer):
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De eind datum van de organisatie. Indien de waarde `null` is, dan is organisatie actief.",
        required=False,
        read_only=True,
    )

    bevoegde_organisaties = BevoegdeOrganisatieSerializer(
        many=True,
        help_text="De bevoegde organisaties. In de lijst van bevoegde organisaties staat minimaal altijd de verantwoordelijke organisatie.",
    )
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
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
            "catalogi": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "Lijst van catalogi die deze organisatie gebruikt.",
            },
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Organisaties/put",
            value={
                "contactWebsite": "http://example.com",
                "contactEmailadres": "user@example.com",
                "contactTelefoonnummer": "31021234567",
                "contactFormulierLink": "http://example.com",
            },
        ),
    ]
)
class LokaleOverheidUpdateSerializer(LokaleOverheidBaseSerializer):
    class Meta:
        model = LokaleOverheid
        fields = (
            "contact_website",
            "contact_emailadres",
            "contact_telefoonnummer",
            "contact_formulier_link",
        )

from rest_framework import serializers

from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokatieListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for locations, including UUID, name and country."""

    class Meta:
        model = Lokatie
        fields = ("uuid", "naam", "land")


class LokatieSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for location details, including contact details, address and opening times."""

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
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        )


class LokaleOverheidListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for municipalities, including uuid and organization."""

    organisatie = serializers.CharField()

    class Meta:
        model = LokaleOverheid
        fields = ("uuid", "organisatie")


class LokaleOverheidSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for municipality details, including organization details, catalogs and locations."""

    organisatie = serializers.CharField()
    lokaties = LokatieListSerializer(many=True)

    bevoegde_organisatie = serializers.CharField()
    ondersteunings_organisatie = serializers.CharField()
    verantwoordelijke_organisatie = serializers.CharField()

    class Meta:
        model = LokaleOverheid
        fields = (
            "uuid",
            "organisatie",
            "lokaties",
            "bevoegde_organisatie",
            "ondersteunings_organisatie",
            "verantwoordelijke_organisatie",
        )

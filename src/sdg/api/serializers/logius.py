from rest_framework import serializers

from sdg.core.models import Overheidsorganisatie


class OverheidsorganisatieSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Overheidsorganisatie, including identifier, label and end date."""

    class Meta:
        model = Overheidsorganisatie
        fields = (
            "owms_identifier",
            "owms_pref_label",
            "owms_end_date",
        )

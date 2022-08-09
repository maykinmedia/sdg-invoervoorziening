from rest_framework import serializers

from sdg.core.models import Overheidsorganisatie


class OverheidsorganisatieSerializer(serializers.HyperlinkedModelSerializer):
    """De ondersteunende organisaties."""

    class Meta:
        model = Overheidsorganisatie
        fields = (
            "owms_identifier",
            "owms_pref_label",
            "owms_end_date",
        )
        extra_kwargs = {
            "owms_identifier": {
                "help_text": "De OWMS Identifier van een de ondersteunende organisatie."
            },
            "owms_pref_label": {
                "help_text": "Het OWMS Prefered Label van een de ondersteunende organisatie."
            },
            "owms_end_date": {
                "help_text": "De einddatum van de ondersteunende organisatie. Indien de waarde `null` is, dan is organisatie actief."
            },
        }

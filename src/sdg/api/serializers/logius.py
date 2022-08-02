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
                "help_text": "Dit is de de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier) van een de ondersteunende organisatie."
            },
            "owms_pref_label": {
                "help_text": "Dit is de de OWMS Prefered Label van een de ondersteunende organisatie."
            },
            "owms_end_date": {
                "help_text": "Dit is de einddatum van de ondersteunende organisatie, als deze null is betekent het dat de ondersteunende organisatie actief is."
            },
        }

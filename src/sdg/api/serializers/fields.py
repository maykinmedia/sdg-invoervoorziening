from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class LabeledUrlSerializer(serializers.Serializer):
    """
    Default serializer for labeled URLs.
    """

    label = serializers.CharField(help_text="Dit veld bevat de label van de URL.")
    url = serializers.URLField(
        help_text="Dit veld bevat de URL naar referentieinformatie over het product."
    )

    def to_internal_value(self, data):
        new_data = {}
        try:
            if not isinstance(data["label"], str):
                raise serializers.ValidationError(
                    _("Label has to be a valid string."),
                )
            new_data["label"] = data.pop("label")
        except KeyError:
            raise serializers.ValidationError(
                _("Verwijzings Link has to have a valid label."),
            )

        try:
            validate = URLValidator()
            validate(data["url"])
            new_data["url"] = data.pop("url")
        except ValidationError:
            raise serializers.ValidationError(
                _("Value has to be a valid url."),
            )
        except KeyError:
            raise serializers.ValidationError(
                _("Verwijzings Link has to have a valid url."),
            )

        if data:
            raise serializers.ValidationError(
                _(f"Verwijzings Link doesn't have key/value pair(s) {data}"),
            )

        return new_data

    def to_representation(self, instance):
        """Split array value into dictionary with label and URL."""
        return {
            "label": instance[0],
            "url": instance[1],
        }


class LabeledUrlListField(LabeledUrlSerializer):
    """
    Default field for a labeled URLs.
    """

    def to_internal_value(self, data):
        if not data:
            return []

        if isinstance(data, list):
            verwijzings_links = []
            if data:
                for verwijzings_link in data:
                    if isinstance(verwijzings_link, dict):
                        verwijzings_links.append(
                            super(LabeledUrlListField, self).to_internal_value(
                                verwijzings_link
                            )
                        )
                    else:
                        raise serializers.ValidationError(
                            _("Give a valid 'label', 'value' instance"),
                        )
            return verwijzings_links

        raise serializers.ValidationError(
            _("Field has to be a list instance"),
        )

    def to_representation(self, value):
        return LabeledUrlSerializer(value, many=True).data

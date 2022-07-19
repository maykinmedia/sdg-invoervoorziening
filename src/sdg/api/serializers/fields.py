from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class LabeledUrlSerializer(serializers.Serializer):
    """
    Default serializer for labeled urls.
    """

    label = serializers.CharField(help_text="Dit veld bevat de label van de url.")
    url = serializers.URLField(
        help_text="Dit velt bevat de url naar relevante informatie over het product."
    )

    def to_representation(self, instance):
        """Split array value into dictionary with label and url."""
        return {
            "label": instance[0],
            "url": instance[1],
        }


@extend_schema_field(LabeledUrlSerializer(many=True))
class LabeledUrlListField(serializers.ListField):
    """
    Default field for a labeled urls.
    """

    def to_representation(self, value):
        """Use serializer to split array value into dictionary with label and url."""
        return LabeledUrlSerializer(value, many=True).data

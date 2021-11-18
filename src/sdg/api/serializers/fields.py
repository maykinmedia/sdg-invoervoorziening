from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class LabeledUrlSerializer(serializers.Serializer):
    """
    Default serializer for labeled urls.
    """

    label = serializers.CharField()
    url = serializers.URLField()

    def to_representation(self, instance):
        """Split array value into dictionary with label and url."""
        return [
            {
                "label": sub_arr[0],
                "url": sub_arr[1],
            }
            for sub_arr in instance
        ]


@extend_schema_field(LabeledUrlSerializer(many=True))
class LabeledUrlListField(serializers.ListField):
    """
    Default field for a labeled urls.
    """

    def to_representation(self, value):
        """Use serializer to split array value into dictionary with label and url."""
        return LabeledUrlSerializer(value, many=True).data

from rest_framework import serializers


class LabeledUrlListField(serializers.ListField):
    """
    Default field for serializing a list of labeled urls.
    """

    def to_representation(self, value):
        """Split array value into dictionary with label and url."""
        return [
            {
                "label": sub_arr[0],
                "url": sub_arr[1],
            }
            for sub_arr in value
        ]

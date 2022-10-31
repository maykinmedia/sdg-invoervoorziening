from unittest import TestCase

from django.contrib.postgres.forms import SimpleArrayField
from django.forms import CharField

from sdg.core.forms import DynamicArrayField


class DynamicArrayFieldTests(TestCase):
    def test_dynamic_array_field_clean(self):
        field = DynamicArrayField(base_field=SimpleArrayField(base_field=CharField()))
        cleaned_data = field.clean(
            [
                "test1, test2",
                "https://google.com",
                "test2, test3",
                "https://google2.com",
            ]
        )
        self.assertEqual(
            cleaned_data,
            [
                ["test1, test2"],
                ["https://google.com"],
                ["test2, test3"],
                ["https://google2.com"],
            ],
        )

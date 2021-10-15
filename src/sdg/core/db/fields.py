from django import forms
from django.contrib.postgres.fields import ArrayField

from sdg.core import forms as sdg_forms


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        return super(ArrayField, self).formfield(
            **{
                "form_class": forms.MultipleChoiceField,
                "choices": self.base_field.choices,
                **kwargs,
            }
        )


class DynamicArrayField(ArrayField):
    def formfield(self, **kwargs):
        return super().formfield(
            **{"form_class": sdg_forms.DynamicArrayField, **kwargs}
        )

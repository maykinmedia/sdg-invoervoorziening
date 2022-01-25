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
    def __init__(self, base_field, size=None, **kwargs):
        self.subwidget_form = kwargs.pop("subwidget_form", None)
        self.single = kwargs.pop("single", False)
        super().__init__(base_field, size, **kwargs)

    def formfield(self, **kwargs):
        if self.subwidget_form:
            kwargs["subwidget_form"] = self.subwidget_form
        return super().formfield(
            **{"form_class": sdg_forms.DynamicArrayField, **kwargs}
        )

    def clean(self, value, model_instance):
        if getattr(self.subwidget_form, "chunk", False):
            value = self.subwidget_form.chunk(value, 2)
        return super().clean(value, model_instance)

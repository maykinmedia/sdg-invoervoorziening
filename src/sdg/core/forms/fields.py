from itertools import chain

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.utils import prefix_validation_error
from django.forms import ChoiceField, Field
from django.utils.translation import gettext_lazy as _

from sdg.core.forms.widgets import BooleanSelect, DynamicArrayWidget
from sdg.producten.constants import BooleanChoices


class DynamicArrayField(forms.Field):
    default_error_messages = {
        "item_invalid": _("Item %(nth)s in de lijst is niet geldig."),
    }

    def __init__(self, base_field, **kwargs):
        self.base_field = base_field
        self.max_length = kwargs.pop("max_length", None)
        self.default = kwargs.pop("default", None)
        subwidget_form = kwargs.pop("subwidget_form", None)

        if isinstance(self.base_field, SimpleArrayField):
            self.base_field.delimiter = "|"

        kwargs.setdefault(
            "widget",
            (
                DynamicArrayWidget(subwidget_form=subwidget_form)
                if subwidget_form
                else DynamicArrayWidget
            ),
        )
        super().__init__(**kwargs)

    def clean(self, value):
        cleaned_data = []
        errors = []
        if value is not None:
            value = [x for x in value if x]

            for index, item in enumerate(value):
                try:
                    cleaned_data.append(self.base_field.clean(item))
                except forms.ValidationError as error:
                    errors.append(
                        prefix_validation_error(
                            error,
                            self.error_messages["item_invalid"],
                            code="item_invalid",
                            params={"nth": index},
                        )
                    )

        if not value:
            cleaned_data = self.default() if callable(self.default) else self.default
        if cleaned_data is None and self.initial is not None:
            cleaned_data = self.initial() if callable(self.initial) else self.initial
        if errors:
            raise forms.ValidationError(list(chain.from_iterable(errors)))
        if not cleaned_data and self.required:
            raise forms.ValidationError(self.error_messages["required"])

        return cleaned_data

    def has_changed(self, initial, data):
        if not data and not initial:
            return False
        return super().has_changed(initial, data)


class BooleanChoiceField(ChoiceField):
    to_python = Field.to_python
    widget = BooleanSelect

    def __init__(self, *, choices=(), **kwargs):
        super().__init__(**kwargs)
        self.choices = choices or BooleanChoices.choices

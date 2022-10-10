from django import template
from django.forms import BaseForm

register = template.Library()


@register.inclusion_tag(
    "components/nonlocalized_form/nonlocalized_form.html", takes_context=True
)
def nonlocalized_form(context, form: BaseForm, **kwargs) -> dict:
    """
    Non-localized Form, built for update view.

    Args:
        - context
        - form: BaseFormSet - form to render.

    Kwargs:
        - [include_form]: bool - Whether to render the form tags.
        - [fields]: string[] - The fields names to render.
    """

    def get_fields() -> list:
        try:
            base_form_fields = form.fields
        except IndexError:
            return []

        fields = kwargs.get("fields")
        if fields:
            return [field for field in base_form_fields if field in fields]
        return base_form_fields

    def get_object_list(form: BaseForm, fields: list) -> list:
        object_list = []
        for field in fields:
            obj = {
                "bound_fields": [form[field]],
                "field": field,
            }
            object_list.append(obj)
        return object_list

    fields = get_fields()

    return {
        **kwargs,
        "context": context,
        "include_form": kwargs.get("include_form", True),
        "form": form,
        "fields": fields,
        "object_list": get_object_list(form, fields),
    }

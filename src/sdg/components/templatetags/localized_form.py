from django import template
from django.forms import BaseFormSet

register = template.Library()


@register.inclusion_tag(
    "components/localized_form/localized_form.html", takes_context=True
)
def localized_form(context, formset: BaseFormSet, **kwargs) -> dict:
    """
    Localized form, built for update view.

    Args:
        - context
        - formset: BaseFormSet - Forms (one for each language) to render.ked.

    Kwargs:
        - [include_form]: bool - Whether to render the form tags.
        - [fields]: string[] - The fields names to render.
    """

    def get_fields() -> list:
        try:
            base_form = formset.forms[0]
            base_form_fields = base_form.fields
        except IndexError:
            return []

        fields = kwargs.get("fields")
        if fields:
            return [field for field in base_form_fields if field in fields]
        return base_form_fields

    def get_languages() -> list:
        languages = [form.initial.get("taal") for form in formset.forms if form.initial.get("taal")]
        return languages or ['nl', 'en']  # FIXME

    def get_object_list(formset: BaseFormSet, fields: list) -> list:
        object_list = []
        languages = get_languages()
        for field in fields:
            obj = {
                "bound_fields": [form[field] for form in formset.forms],
                "field": field,
            }
            for index, language in enumerate(languages):
                obj["bound_fields"][index].language = language
            object_list.append(obj)
        return object_list

    fields = get_fields()

    return {
        **kwargs,
        "context": context,
        "include_form": kwargs.get("include_form", True),
        "formset": formset,
        "fields": fields,
        "languages": get_languages(),
        "object_list": get_object_list(formset, fields),
    }

from django import template

register = template.Library()


@register.inclusion_tag("components/fields/checkbox.html", takes_context=True)
def checkbox(context, field, **kwargs):
    """
    Checkbox field, built for update view.

    Args:
        - context
        - field

    Kwargs:
        - as_row, define if the checkbox field is placed inside a tr and td.
        - inline, define if the checkbox field is rendered inline.
    """

    as_row = kwargs.get("as_row", True)
    inline = kwargs.get("inline", False)

    return {
        **kwargs,
        "context": context,
        "field": field,
        "as_row": as_row,
        "inline": inline,
    }


@register.inclusion_tag("components/fields/core.html", takes_context=True)
def core(context, label, tooltip, value=None, field=None, **kwargs):
    """
    Core (read-only) field, built for update view.

    Args:
        - context
        - label
        - tooltip
        - value
        - field

    Kwargs:
        - as_row, define if the core field is placed inside a tr and td.
        - inline, define if the core field is rendered inline.
        - fallback_value, define if there is a possibility that value can be falsy
    """

    inline = kwargs.get("inline", False)
    as_row = kwargs.get("as_row", True)
    fallback_value = kwargs.get("fallback_value", None)

    return {
        **kwargs,
        "context": context,
        "label": label,
        "as_row": as_row,
        "tooltip": tooltip,
        "value": value,
        "field": field,
        "fallback_value": fallback_value,
        "inline": inline,
    }


@register.inclusion_tag("components/fields/localized.html", takes_context=True)
def localized(context, object, **kwargs):
    """
    Localized field, built for update view.

    Args:
        - context
        - object, containing the bound_fields to render

    Kwargs:
        - as_row, define if the localized field is placed inside a tr and td.
        - inline, define if the localized field is rendered inline.
    """

    inline = kwargs.get("inline", False)
    as_row = kwargs.get("as_row", True)

    return {
        **kwargs,
        "context": context,
        "as_row": as_row,
        "inline": inline,
        "object": object,
    }


@register.inclusion_tag("components/fields/localized_url.html", takes_context=True)
def localized_url(context, form, **kwargs):
    """
    Localized url field, built for update view.

    Args:
        - context
        - form, the form property to extract some date from.

    Kwargs:
        - as_row, define if the localized url field is placed inside a tr and td.
    """

    as_row = kwargs.get("as_row", True)

    def object_format(form):
        return {
            "label": form["decentrale_procedure_label"],
            "link": form["decentrale_procedure_link"],
            "language": form["taal"].value,
        }

    def get_object_list(forms):
        object_list = [object_format(form) for form in forms]
        return object_list

    return {
        "context": context,
        "bound_fields": get_object_list(form.forms),
        "form": form,
        "as_row": as_row,
    }


@register.inclusion_tag("components/fields/nonlocalized.html", takes_context=True)
def nonlocalized(context, object, **kwargs):
    """
    Non-localized field, built for update view.

    Args:
        - context
        - object, containing the bound_fields to render

    Kwargs:
        - as_row, define if the non-localized field is placed inside a tr and td.
        - inline, define if the non-localized field is rendered inline.
    """

    as_row = kwargs.get("as_row", True)
    inline = kwargs.get("inline", False)

    return {
        **kwargs,
        "context": context,
        "as_row": as_row,
        "object": object,
        "inline": inline,
    }


@register.inclusion_tag("components/fields/select.html", takes_context=True)
def select(context, field, **kwargs):
    """
    Select field, built for update view.

    Args:
        - context
        - field

    Kwargs:
        - as_row, define if the select field is placed inside a tr and td.
        - inline, define if the select field is rendered inline.

    """

    as_row = kwargs.get("as_row", True)
    inline = kwargs.get("inline", False)
    hide_element = kwargs.get("hide_element", False)

    return {
        **kwargs,
        "context": context,
        "field": field,
        "as_row": as_row,
        "inline": inline,
        "hide_element": hide_element,
    }


@register.inclusion_tag("components/fields/readonly.html", takes_context=True)
def readonly(context, object, **kwargs):
    """
    Readonly field, built for update view.

    Args:
        - context
        - object, containing the bound_fields to render

    Kwargs:
        - as_row, define if the readonly field is placed inside a tr and td.
    """

    as_row = kwargs.get("as_row", True)

    return {
        **kwargs,
        "context": context,
        "as_row": as_row,
        "object": object,
    }

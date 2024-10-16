from django import template

from sdg.producten.types import Language, ProductFieldMetadata

register = template.Library()


@register.filter
def get_field(instance, field_name):
    if not instance:
        return None

    return instance.get_field(field_name)


@register.filter
def get(instance, field_name):
    if not instance:
        return None

    return getattr(instance, field_name)


@register.filter
def value(field):
    return field.value


@register.filter
def exclude(field_list: list, excluded_fields: str) -> list:
    excluded_fields = set(excluded_fields.split(","))

    result = []
    for field in field_list:
        field_name = field.name.lower()
        if field_name not in excluded_fields:
            result.append(field)
        else:
            excluded_fields.discard(field_name)

    if excluded_fields:
        raise RuntimeError(
            "Invalid field in excluded field list: {excluded}. Available fields: {available}".format(
                excluded=", ".join(excluded_fields),
                available=", ".join([f.name.lower() for f in field_list]),
            )
        )

    return result


@register.inclusion_tag("producten/_include/field_info.html")
def field_info(field: ProductFieldMetadata, **kwargs):
    return {**kwargs, "field": field}

from django import template

register = template.Library()


@register.filter
def get_field(instance, field_name):
    return instance.get_field(field_name)


@register.filter
def value(field):
    return field.value


@register.filter
def exclude(field_list: list, excluded_fields: str) -> list:
    return [f for f in field_list if f.name.lower() not in excluded_fields.split(",")]

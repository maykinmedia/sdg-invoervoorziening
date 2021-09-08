from django import template

register = template.Library()


@register.filter
def get_field(instance, field_name):
    return instance.get_field(field_name)


@register.filter
def value(field):
    return field.value

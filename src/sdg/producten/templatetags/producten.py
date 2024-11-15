from django import template

from sdg.producten.types import ProductFieldMetadata

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


@register.inclusion_tag("producten/_include/field_info.html")
def field_info(field: ProductFieldMetadata, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("producten/_include/publications.html")
def publications(product, publication_links, concept_url):
    return {
        "product": product,
        "publication_links": publication_links,
        "concept_url": concept_url,
    }

from datetime import date, timedelta
from typing import Literal

from django import template

from sdg.producten.models import Product
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


@register.inclusion_tag("producten/_include/doordruk_warning.html")
def doordruk_warning(product: Product):
    def return_value(show_warning, warning_date):
        return {
            "doordruk_activation_warning": show_warning,
            "datum__doordrukken": warning_date,
        }

    reference_product = product.reference_product
    reference_auto_press_through = reference_product.automatisch_doordrukken
    reference_auto_press_through_date = reference_product.automatisch_doordrukken_datum
    product_press_through = product.automatisch_doordrukken

    if product.is_referentie_product:
        return return_value(None, None)

    if not reference_auto_press_through or not reference_auto_press_through_date:
        return return_value(None, None)

    if not date.today() >= reference_auto_press_through_date - timedelta(days=30):
        return return_value(None, None)

    if reference_auto_press_through and not product_press_through:
        return return_value(False, reference_auto_press_through_date)

    return return_value(True, reference_auto_press_through_date)

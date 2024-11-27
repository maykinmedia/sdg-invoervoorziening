from datetime import date, timedelta

from django import template

from sdg.producten.types import ProductFieldMetadata

from sdg.producten.models import Product

from typing import Literal

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
    doordruk_activation_warning: bool | None
    is_reference_product = product.is_referentie_product
    auto_forward = product.automatisch_doordrukken
    ref_auto_forward_date = product.automatisch_doordrukken_datum

    if is_reference_product:
        doordruk_activation_warning = None

    else:
        reference_product: Product = product.referentie_product
        ref_auto_forward = reference_product.automatisch_doordrukken
        ref_auto_forward_date = reference_product.automatisch_doordrukken_datum
        original_publication_date = reference_product.automatisch_doordrukken_datum - timedelta(days=30)
        warning_in_timeframe = date.today() >= original_publication_date

        # When it isn't the right time yet, don't show the warning.
        if not warning_in_timeframe:
            doordruk_activation_warning = None    
        elif auto_forward and ref_auto_forward:
            doordruk_activation_warning = True
        elif not auto_forward and ref_auto_forward:
            doordruk_activation_warning = False
        else: 
            doordruk_activation_warning = None

    return {
        "doordruk_activation_warning": doordruk_activation_warning,
        "datum__doordrukken": ref_auto_forward_date
    }
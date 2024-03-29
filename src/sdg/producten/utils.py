from datetime import datetime
from functools import lru_cache
from typing import List

from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import gettext as _

from sdg.conf.utils import org_type_cfg
from sdg.core.constants import TaalChoices
from sdg.producten.types import _code_to_flag


def is_past_date(date: datetime.date) -> bool:
    """Checks if a date is in the past."""
    return date < now().date()


def duplicate_localized_products(form, new_version):
    """Duplicates localized products into new product version."""
    from sdg.producten.models import LocalizedProduct

    localized_products = []
    for subform in form:
        product = subform.save(commit=False)
        product.product_versie = new_version
        product.pk = None
        localized_products.append(product)
    return LocalizedProduct.objects.bulk_create(localized_products)


def build_url_kwargs(product, catalog=None) -> dict:
    """Return url kwargs for product."""
    pk = catalog.lokale_overheid.pk if catalog else product.catalogus.lokale_overheid.pk
    catalog_pk = catalog.pk if catalog else product.catalogus.pk
    return {
        "pk": pk,
        "catalog_pk": catalog_pk,
        "product_pk": product.pk,
    }


def parse_changed_data(changed_data, *, form, language=None) -> List[dict]:
    """Parse changed data into correct JSON for `ProductVersie.bewerkte_velden`."""

    return [
        {
            "language": language,
            "flag": _code_to_flag(language),
            "label": str(form.fields[field].label),
            "field": field,
        }
        for field in changed_data
    ]


@lru_cache
def get_placeholder_maps(product):
    """
    Get placeholder text mappings for a municipality's product.
    """
    available_explanation_map = {}
    falls_under_explanation_map = {}

    generic_product = product.generiek_product
    municipality = product.catalogus.lokale_overheid

    for language in TaalChoices.get_available_languages():
        generic_languages = generic_product.vertalingen.all()
        result = [i for i in generic_languages if i.taal == language]  # avoid query
        localized_generic_product = result[0]

        with translation.override(language):
            available_explanation_map[language] = _(
                "In de {org_type_name} {lokale_overheid} is {product} onderdeel van [product]."
            ).format(
                org_type_name=org_type_cfg().name,
                lokale_overheid=municipality,
                product=localized_generic_product,
            )
            falls_under_explanation_map[language] = _(
                "De {org_type_name} {lokale_overheid} levert het product {product} niet."
            ).format(
                org_type_name=org_type_cfg().name,
                lokale_overheid=municipality,
                product=localized_generic_product,
            )

    return available_explanation_map, falls_under_explanation_map

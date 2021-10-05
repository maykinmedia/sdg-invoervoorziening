from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.utils.timezone import now


def is_past_date(date: datetime) -> bool:
    """Checks if a date is in the past ignoring seconds."""
    if date.replace(second=0, microsecond=0) < now().replace(second=0, microsecond=0):
        return True
    else:
        return False


@dataclass
class ProductField:
    name: str
    verbose_name: str
    value: Any
    help_text: str
    is_reference: bool
    is_markdown: bool


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

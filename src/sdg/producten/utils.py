from datetime import datetime

from django.utils.timezone import now


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

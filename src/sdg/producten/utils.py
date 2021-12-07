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


def build_url_kwargs(product) -> dict:
    """Return url kwargs for product."""
    return {
        "pk": product.catalogus.lokale_overheid.pk,
        "catalog_pk": product.catalogus.pk,
        "product_pk": product.pk,
    }

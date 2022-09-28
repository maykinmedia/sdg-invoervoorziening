import datetime

from django.core.management import BaseCommand

from sdg.core.constants import GenericProductStatus
from sdg.producten.models import GeneriekProduct, Product
from sdg.producten.models.localized import LocalizedGeneriekProduct


def _generate_status(generic_product: GeneriekProduct):
    """
    Generate the status of a generic product based on custom logic.
    """
    try:
        reference_product_has_active_version = bool(
            Product.objects.get(
                catalogus__is_referentie_catalogus=True,
                generiek_product=generic_product,
            ).active_version
        )
    except Product.DoesNotExist:
        reference_product_has_active_version = None

    localized_generic_texts = all(
        LocalizedGeneriekProduct.objects.filter(
            generiek_product=generic_product
        ).values_list("generieke_tekst", flat=True)
    )

    if generic_product.upn.is_verwijderd and not generic_product.eind_datum:
        return GenericProductStatus.EXPIRED
    elif generic_product.eind_datum:
        if generic_product.eind_datum > datetime.date.today():
            return GenericProductStatus.EOL
        if generic_product.eind_datum <= datetime.date.today():
            return GenericProductStatus.DELETED
    elif localized_generic_texts:
        if reference_product_has_active_version is None:
            return GenericProductStatus.MISSING
        elif reference_product_has_active_version:
            return GenericProductStatus.READY_FOR_PUBLICATION
        else:
            return GenericProductStatus.READY_FOR_ADMIN
    else:
        return GenericProductStatus.NEW


class Command(BaseCommand):
    help = "Update status for all generic products"

    def handle(self, **options):
        updated_product_count = 0

        for generic_product in GeneriekProduct.objects.all():
            generic_product.product_status = _generate_status(generic_product)
            generic_product.save()
            updated_product_count += 1

        self.stdout.write(
            f"Updated status for {updated_product_count} generic products."
        )

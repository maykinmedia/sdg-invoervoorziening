from datetime import date

from django.core.management import BaseCommand

from sdg.producten.models import Product, ProductVersie


class Command(BaseCommand):
    help = "Druk referentie teksten door op de gerelateerde producten."

    # Reset DB data that indicates an active press through.
    def reset_press_through_data(self, products):
        products.update(
            automatisch_doordrukken=False,
            automatisch_doordrukken_datum=None,
        )

    def handle(self, *args, **options):
        reference_products = Product.objects.filter(
            referentie_product__isnull=True,
            automatisch_doordrukken=True,
            automatisch_doordrukken_datum__lte=date.today(),
        )
        for reference_product in reference_products:
            reference_product_version: ProductVersie = (
                reference_product.most_recent_version
            )
            # All products linked to the reference product.
            products = Product.objects.filter(
                referentie_product_id=reference_product.pk,
                automatisch_doordrukken=True,
                automatisch_doordrukken_datum__lte=date.today(),
            )
            # Update each product linked to the reference product.
            for product in products:
                product_version: ProductVersie = product.most_recent_version
                product_version.update_with_reference_texts(
                    reference_product_version=reference_product_version
                )
            # Reset press through attributes on products.
            self.reset_press_through_data(products=products)
        # Reset press through attributes on reference products.
        self.reset_press_through_data(products=reference_products)

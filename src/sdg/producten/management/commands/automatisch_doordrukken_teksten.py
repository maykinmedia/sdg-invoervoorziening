from datetime import date

from django.core.management import BaseCommand

from sdg.producten.models import Product, ProductVersie


class Command(BaseCommand):
    help = "Druk referentie teksten door op de gerelateerde producten."

    # Reset DB data that indicates an active press through.
    def reset_press_through_data(self, products):
        count = products.count()
        products.update(
            automatisch_doordrukken=False,
            automatisch_doordrukken_datum=None,
        )
        self.stdout.write(f"Reset press through data for {count} products")

    def handle(self, *args, **options):
        self.stdout.write("Starting reference text press through process...")

        reference_products = Product.objects.filter(
            referentie_product__isnull=True,
            automatisch_doordrukken=True,
            automatisch_doordrukken_datum__lte=date.today(),
        )

        reference_count = reference_products.count()
        self.stdout.write(f"Found {reference_count} reference products to process")

        if reference_count == 0:
            self.stdout.write(
                self.style.WARNING("No reference products found for processing")
            )
            return

        total_updated_products = 0

        for reference_product in reference_products:
            self.stdout.write(f"Processing reference product: {reference_product.pk}")

            reference_product_version: ProductVersie = (
                reference_product.most_recent_version
            )

            # All products linked to the reference product.
            products = Product.objects.filter(
                referentie_product_id=reference_product.pk,
                automatisch_doordrukken=True,
                automatisch_doordrukken_datum__lte=date.today(),
            )

            product_count = products.count()
            self.stdout.write(f"  Found {product_count} linked products to update")

            # Update each product linked to the reference product.
            for product in products:
                self.stdout.write(f"    Updating product: {product.pk}")
                product_version: ProductVersie = product.most_recent_version
                product_version.update_with_reference_texts(
                    reference_product_version=reference_product_version
                )
                total_updated_products += 1

            # Reset press through attributes on products.
            if product_count > 0:
                self.reset_press_through_data(products=products)

        # Reset press through attributes on reference products.
        self.stdout.write("Resetting press through data for reference products")
        self.reset_press_through_data(products=reference_products)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully completed! Updated {total_updated_products} products "
                f"from {reference_count} reference products"
            )
        )

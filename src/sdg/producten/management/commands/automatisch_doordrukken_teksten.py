from datetime import date

from django.core.management import BaseCommand

from sdg.producten.models import Product, ProductVersie


class Command(BaseCommand):
    help = "Druk referentie teksten door op de gerelateerde producten."

    def press_through_reference_text(
        self, product: Product, referentie_product: Product
    ):
        most_recent_product_version: ProductVersie = product.most_recent_version
        most_recent_product_version.update_with_reference_texts(
            reference_product_version=referentie_product
        )

    def reset_pass_through_attributes(self, product: Product):
        product.automatisch_doordrukken = False
        product.automatisch_doordrukken_datum = None
        product.doordrukken_action_taken = False
        product.save()

    def handle(self, *args, **options):
        for referentie_product in Product.objects.filter(
            referentie_product__isnull=True,
            automatisch_doordrukken=True,
            automatisch_doordrukken_datum__lte=date.today(),
        ):
            active_reference_product_version = referentie_product.active_version
            # Get all products related to the reference product
            for product in Product.objects.filter(
                referentie_product_id=referentie_product.pk,
                automatisch_doordrukken=True,
                automatisch_doordrukken_datum__lte=date.today(),
            ):
                self.reset_pass_through_attributes(product)

                if product.doordrukken_action_taken is False:
                    self.press_through_reference_text(
                        product, referentie_product=active_reference_product_version
                    )

            self.reset_pass_through_attributes(referentie_product)

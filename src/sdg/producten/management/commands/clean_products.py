from django.core.management import BaseCommand

from sdg.producten.models import Product


class Command(BaseCommand):
    help = "Clean all products according to standard rules."

    def handle(self, **options):
        products = Product.objects.all()
        products.prefetch_related("versies", "versies__vertalingen")

        for product in products:
            self.stdout.write(f"Cleaning product {product.uuid}")
            product = self.clean_product(product)
            product.save()

    @staticmethod
    def clean_product_explanations(product):
        return product

    def clean_product(self, product):
        """
        Clean a product.
        """
        product = self.clean_product_explanations(product)
        return product

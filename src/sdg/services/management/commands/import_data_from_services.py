from django.core.management import BaseCommand

from sdg.producten.models import GeneriekProduct


class Command(BaseCommand):
    help = "Retrieve all configured APIs and fill generic products."

    def handle(self, **options):
        from sdg.services.utils import retrieve_service_data

        # data = retrieve_service_data()
        generic_products = []
        # TODO: fill `generic_products` list
        GeneriekProduct.objects.bulk_create(generic_products)

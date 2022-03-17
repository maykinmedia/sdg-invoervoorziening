from datetime import datetime

from django.core.management import BaseCommand

from sdg.producten.models import LocalizedGeneriekProduct
from sdg.services.models import ServiceConfiguration


class Command(BaseCommand):
    help = "Retrieve all configured APIs and fill generic products."

    def handle(self, **options):
        updated_objects = 0

        for service_config in ServiceConfiguration.objects.all():
            products = service_config.retrieve_products()

            for product in products:
                localized_generic_products = LocalizedGeneriekProduct.objects.filter(
                    generiek_product__doelgroep=service_config.doelgroep,
                    generiek_product__upn__upn_label=product["upnLabel"],
                    taal=product["taal"],
                )
                updated_objects += localized_generic_products.update(
                    product_titel=product["titel"],
                    generieke_tekst=product["tekst"],
                    verwijzing_links=[list(i.values())[:2] for i in product["links"]],
                    landelijke_link=product["url"],
                    datum_check=datetime.fromisoformat(product["laatstGecheckt"]),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {updated_objects} localized generic products."
            )
        )

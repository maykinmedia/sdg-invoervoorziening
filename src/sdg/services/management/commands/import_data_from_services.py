from datetime import datetime

from django.core.management import BaseCommand
from django.db import connection

from sdg.core.models import UniformeProductnaam
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
                    generiek_product__upn__upn_uri=product["upnUri"],
                    taal=product["taal"],
                )
                self.stdout.write(
                    f"Updating translations for generic product '{product['upnUri']}' via {service_config}."
                )

                updated_objects += localized_generic_products.update(
                    product_titel=product["titel"],
                    generieke_tekst=product["tekst"],
                    verwijzing_links=[list(i.values())[:2] for i in product["links"]],
                    landelijke_link=product["url"],
                    datum_check=datetime.fromisoformat(product["laatstGecheckt"]),
                )

        self.clean_upn_data()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {updated_objects} localized generic products."
            )
        )

    def clean_upn_data(self):
        """
        Delete the related Generic Product objects that do not match the UPN requirements:

        - If there are SDG-codes: delete the Generic Product that does not have doelgroep.
        - If there are no SDG-codes: delete the Generic Product that have a doelgroep.

        * If there are any related products they must be deleted manually.
        """
        upn_qs = UniformeProductnaam.objects.all()
        upn_qs.prefetch_related(
            "generieke_producten",
            "generieke_producten__producten",
        )
        for upn in upn_qs:
            if upn.sdg:
                generic_products = [
                    i for i in upn.generieke_producten.all() if not i.doelgroep
                ]
            else:
                generic_products = [
                    i for i in upn.generieke_producten.all() if i.doelgroep
                ]

            for generic_product in generic_products:
                if generic_product.producten.all():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Generic product '{generic_product}' has related products. Delete manually."
                        )
                    )
                else:
                    generic_product.delete()

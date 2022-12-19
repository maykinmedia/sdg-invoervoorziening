import logging
from datetime import datetime

from django.core.management import BaseCommand

from sdg.core.models import Overheidsorganisatie
from sdg.producten.models import LocalizedGeneriekProduct
from sdg.services.models import ServiceConfiguration

logger = logging.getLogger(__name__)


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
                    verwijzing_links=[
                        [
                            item["label"],
                            item["url"],
                            item["categorie"],
                        ]
                        for item in product["links"]
                    ],
                    landelijke_link=product["url"],
                    datum_check=datetime.fromisoformat(product["laatstGecheckt"]),
                    laatst_gewijzigd=datetime.fromisoformat(product["laatstGewijzigd"]),
                    uuid=product["id"],
                )

                # Update organizations with their role.
                if (
                    first_localized_generic_product := localized_generic_products.first()
                ):
                    generiek_product = first_localized_generic_product.generiek_product
                    generiek_product.verantwoordelijke_organisaties.clear()

                    for org in product["organisaties"]:
                        org_obj = Overheidsorganisatie.objects.filter(
                            owms_identifier=org["owmsUri"]
                        ).first()
                        if not org_obj:
                            logger.error(
                                f"Could not find government organization with OWMS URI: {org['owmsUri']}"
                            )
                            continue

                        generiek_product.verantwoordelijke_organisaties.add(
                            org_obj, through_defaults={"rol": org["rol"]}
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {updated_objects} localized generic products."
            )
        )

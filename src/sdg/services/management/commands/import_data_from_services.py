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
        for service_config in ServiceConfiguration.objects.all():
            products = service_config.retrieve_products()

            # Empty non-existing generic texts. These texts could have been
            # present at first but removed at a later point in time. We need to
            # reflect that change here.
            retrieved_upn_uris = [p["upnUri"] for p in products]
            LocalizedGeneriekProduct.objects.filter(
                generiek_product__doelgroep=service_config.doelgroep,
            ).exclude(
                generiek_product__upn__upn_uri__in=retrieved_upn_uris,
            ).update(
                # Don't clean everything to prevent manually entered texts from
                # being wiped.
                #
                # product_titel="",
                # generieke_tekst="",
                # verwijzing_links=[],
                # landelijke_link="",
                # datum_check=None,
                # laatst_gewijzigd=None,
                uuid=None,
            )

            for product in products:
                try:
                    localized_generic_product = LocalizedGeneriekProduct.objects.get(
                        generiek_product__doelgroep=service_config.doelgroep,
                        generiek_product__upn__upn_uri=product["upnUri"],
                        taal=product["taal"],
                    )
                    self.stdout.write(
                        f"Updating translations for generic product '{product['upnUri']}' via {service_config}."
                    )
                except LocalizedGeneriekProduct.DoesNotExist:
                    logger.debug(
                        f"Generic product with UPN URI '{product['upnUri']}' does not exist."
                    )
                    continue

                localized_generic_product.product_titel = product["titel"]
                localized_generic_product.generieke_tekst = product["tekst"]
                localized_generic_product.verwijzing_links = [
                    [
                        item["label"],
                        item["url"],
                        item["categorie"],
                    ]
                    for item in product.get("links", [])
                ]
                localized_generic_product.landelijke_link = product["url"]

                # An undocumented change in the API of Ondernemersplein removed the
                # attribute "laatstGecheckt" entirely.
                last_checked = product.get("laatstGecheckt", None)
                if last_checked:
                    localized_generic_product.datum_check = datetime.fromisoformat(
                        product["laatstGecheckt"]
                    )
                localized_generic_product.laatst_gewijzigd = datetime.fromisoformat(
                    product["laatstGewijzigd"]
                )
                localized_generic_product.uuid = product["id"]
                localized_generic_product.save()

                # Update organizations with their role.
                generiek_product = localized_generic_product.generiek_product
                generiek_product.verantwoordelijke_organisaties.clear()

                # Sometimes, the "organisaties" key is none instead of an empty list.
                if not product["organisaties"]:
                    continue

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
            self.style.SUCCESS("Successfully updated localized generic products.")
        )

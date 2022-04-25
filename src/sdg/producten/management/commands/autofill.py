from django.core.management import BaseCommand
from django.db.models import Count

from sdg.core.constants import TaalChoices
from sdg.core.models import ProductenCatalogus, UniformeProductnaam
from sdg.organisaties.models import BevoegdeOrganisatie
from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)


class Command(BaseCommand):
    help = "Generate generic and specific (reference) products and fill catalogs where needed."

    def handle(self, **options):
        # Get all catalogs that can be filled and store matching fields.
        catalogs = []
        for catalog in ProductenCatalogus.objects.filter(
            autofill=True, is_referentie_catalogus=True
        ):
            fields = [f.lower() for f in catalog.autofill_upn_filter]
            if fields:
                catalogs.append((catalog, fields))

        # Iterate over the UPL, create generic (+localized) and specific
        # (+localized, +version) products if they don't exist yet.

        # NOTE: New languages are not created automatically. There's no need
        # for this feature at the moment.
        for upn in UniformeProductnaam.objects.annotate(Count("generieke_producten")):
            if upn.generieke_producten__count == 0:
                generic_product = GeneriekProduct.objects.create(upn=upn)
                LocalizedGeneriekProduct.objects.localize(
                    instance=generic_product,
                    languages=TaalChoices.get_available_languages(),
                )
                self.stdout.write(f'Created new generic product for "{upn}".')

                generic_products = [generic_product]
            else:
                generic_products = upn.generieke_producten.all()

            active_fields = upn.get_active_fields()

            for catalog, autofill_fields in catalogs:

                default_auth_org = BevoegdeOrganisatie.objects.filter(
                    lokale_overheid=catalog.lokale_overheid
                ).first()
                # Fix missing default authorized organisation.
                if default_auth_org is None:
                    default_auth_org = BevoegdeOrganisatie.objects.create(
                        lokale_overheid=catalog.lokale_overheid,
                        organisatie=catalog.lokale_overheid.organisatie,
                    )

                if all(f in active_fields for f in autofill_fields):
                    # Typically, there is only 1 generic product but there
                    # could be more if they were manually added.
                    for generic_product in generic_products:
                        # Typically, if a generic product was created with this
                        # flow, there's always a product present in the
                        # reference catalog(s). If the catalog autofill fields
                        # changed, or a new catalog was added, we need to update
                        # their products as well.
                        product, p_created = Product.objects.get_or_create(
                            generiek_product=generic_product,
                            catalogus=catalog,
                            defaults={"bevoegde_organisatie": default_auth_org},
                        )
                        if p_created:
                            version = ProductVersie.objects.create(
                                product=product, publicatie_datum=None
                            )
                            LocalizedProduct.objects.localize(
                                instance=version,
                                languages=TaalChoices.get_available_languages(),
                            )

                            self.stdout.write(
                                f'Created new product "{upn}" in catalog "{catalog}".'
                            )

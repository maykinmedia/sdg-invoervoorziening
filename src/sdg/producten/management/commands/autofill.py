from django.core.management import BaseCommand

from sdg.core.constants import TaalChoices
from sdg.core.models import ProductenCatalogus, UniformeProductnaam
from sdg.organisaties.models import BevoegdeOrganisatie
from sdg.producten.models import LocalizedProduct, Product, ProductVersie


class Command(BaseCommand):
    help = "Create reference products, based on generic products, for all reference catalogs where appropriate."

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
        for upn in UniformeProductnaam.objects.filter(is_verwijderd=False):

            generic_products = list(upn.generieke_producten.all())
            active_fields = upn.get_active_fields()

            for catalog, autofill_fields in catalogs:

                default_auth_org = BevoegdeOrganisatie.objects.filter(
                    lokale_overheid=catalog.lokale_overheid,
                    organisatie=catalog.lokale_overheid.organisatie,
                ).first()
                # Fix missing default authorized organisation.
                if default_auth_org is None:
                    default_auth_org = BevoegdeOrganisatie.objects.create(
                        lokale_overheid=catalog.lokale_overheid,
                        organisatie=catalog.lokale_overheid.organisatie,
                    )
                    self.stdout.write(
                        f'Corrected missing default bevoegde organisatie for "{catalog.lokale_overheid}".'
                    )

                if all(f in active_fields for f in autofill_fields):
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
                        if p_created or product.versies.count() == 0:
                            # In case there are no versions, someone manually
                            # deleted them as this is the only way to create
                            # products in the reference catalogs.
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

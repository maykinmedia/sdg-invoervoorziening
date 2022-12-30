import datetime
import string

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

    def _get_group(self, sdg_code: str) -> str:
        """Get the target group from a given SDG code.
        - The range A-I equals "burger".
        - The range J+ equals "bedrijf".
        """
        letter = sdg_code[0]
        if letter in string.ascii_uppercase[:9]:
            return "eu-burger"
        elif letter in string.ascii_uppercase[9:]:
            return "eu-bedrijf"

    def _get_or_create_valid_generic_products(self, upn):
        """
        Retrieve a list of all generic products that belong to this UPN. At the
        moment this can be 0, 1 or 2. If a UPN is not meant for the SDG, the
        result will be 0. If the UPN contains 2 SDG codes that belong to
        different target groups (eu-burger or eu-bedrijf), the result will be
        2 generic products.

        Missing generic products will be created.
        """
        # NOTE: This part is really SDG specific and deviates from the
        # generic feature of the autofill-fields. We need the SDG code(s)
        # to decide which generic product(s) to create.

        # Create generic product (and localize) for each target group
        groups = [doelgroep for i in upn.sdg if (doelgroep := self._get_group(i))]

        generic_products = []
        for group in groups:
            (generic_product, g_created,) = GeneriekProduct.objects.get_or_create(
                upn=upn,
                doelgroep=group,
            )
            generic_products.append(generic_product)

            if g_created:
                self.stdout.write(f'Created new generic product for "{upn} ({group})".')
                LocalizedGeneriekProduct.objects.localize(
                    instance=generic_product,
                    languages=TaalChoices.get_available_languages(),
                )

        return generic_products

    def _clean_other_generic_products(self, upn, valid_generic_products):
        """
        Set an end date on generic products (attached to given UPN) that are
        not in the list of `valid_generic_products`

        It's possible existing generic products were created when the UPN had
        different properties (like an SDG code that was later removed). These
        generic products need to be cleaned up. We cannot just delete them,
        since they have relations and we should not delete anything that could
        have user data.
        """
        correct_gp_pks = [gp_i.pk for gp_i in valid_generic_products]
        for existing_gp in list(upn.generieke_producten.all()):
            if existing_gp.pk not in correct_gp_pks:
                self.stdout.write(
                    f'Marking old generic product for "{upn} ({existing_gp.pk}) as removed".'
                )
                existing_gp.eind_datum = datetime.date.today()
                existing_gp.save()

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

                    # NOTE: The function below uses SDG specific logic,
                    # ingoring the more generic "autofill_fields" feature.
                    generic_products = self._get_or_create_valid_generic_products(upn)
                    self._clean_other_generic_products(upn, generic_products)

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

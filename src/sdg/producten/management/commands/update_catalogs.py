import datetime

from django.core.management import BaseCommand

from sdg.core.constants import TaalChoices
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import BevoegdeOrganisatie, LokaleOverheid
from sdg.producten.models import Product, ProductVersie
from sdg.producten.models.localized import LocalizedProduct


class Command(BaseCommand):
    help = "Creates, updates and corrects catalogs with products based on reference catalogs, for each active organisation."

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--organisation",
            help="Enforce a specific plugin to be used. Defaults to the configured plugin.",
        )
        parser.add_argument(
            "--fill-empty-english-text",
            help="Fill only empty English texts with reference texts.",
            action="store_true",
        )

    def handle(self, **options):
        _org_param = options.get("organisation")
        _fill_empty_english_text = options.get("fill_empty_english_text")

        product_catalog_query_kwargs = {}
        if _org_param:
            local_government = LokaleOverheid.objects.filter(
                organisatie__owms_pref_label__iexact=_org_param
            ).first()

            if local_government is None:
                self.stderr.write(f"Cannot find organisation: {_org_param}")
                return

            self.stdout.write(f"Filtering on organisation: {local_government}")

            product_catalog_query_kwargs.update({"lokale_overheid": local_government})

        created_catalogs = 0

        # Create catalogs, based on reference catalogs, for each local
        # government.
        for local_government in LokaleOverheid.objects.filter(
            automatisch_catalogus_aanmaken=True, organisatie__owms_end_date=None
        ):
            # Create a specific catalog (if it doesn't exist) for each reference catalog.
            for reference_catalog in ProductenCatalogus.objects.filter(
                is_referentie_catalogus=True
            ):
                catalog, is_created = ProductenCatalogus.objects.get_or_create(
                    referentie_catalogus=reference_catalog,
                    lokale_overheid=local_government,
                    defaults={
                        "is_referentie_catalogus": False,
                        "is_default_catalogus": True,
                        "domein": reference_catalog.domein,
                        "versie": reference_catalog.versie,
                        "naam": f"{local_government} ({reference_catalog.naam})",
                    },
                )
                if is_created:
                    created_catalogs += 1
                    self.stdout.write(
                        f"Created new catalog '{catalog.naam}' for '{local_government}'."
                    )

        created_products = 0

        current_count = 0
        total = (
            Product.objects.filter(catalogus__is_referentie_catalogus=True).count()
            * ProductenCatalogus.objects.filter(
                is_referentie_catalogus=False, **product_catalog_query_kwargs
            ).count()
        )

        def perc(count):
            return "{:0d}%".format(int(100.0 / total * count))

        # Iterate over all reference catalogs. Typically, this is only the SDG
        # catalog.
        for reference_catalog in ProductenCatalogus.objects.filter(
            is_referentie_catalogus=True
        ):

            # Iterate over all reference products in the reference catalog.
            for reference_product in reference_catalog.producten.all():
                active_reference_product_version = reference_product.active_version

                if not active_reference_product_version:
                    self.stdout.write(
                        f"[{perc(current_count)}] Processing reference product '{reference_product}' without any active version to get translations from..."
                    )
                else:
                    self.stdout.write(
                        f"[{perc(current_count)}] Processing reference product '{reference_product}'..."
                    )

                # Iterate over all (specific) catalogs that belong to the current
                # reference catalog.
                for catalog in ProductenCatalogus.objects.filter(
                    referentie_catalogus=reference_catalog,
                    **product_catalog_query_kwargs,
                ):
                    corrections = []

                    default_auth_org = BevoegdeOrganisatie.objects.filter(
                        lokale_overheid=catalog.lokale_overheid
                    ).first()

                    # Fix missing default authorized organisation.
                    if default_auth_org is None:
                        default_auth_org = BevoegdeOrganisatie.objects.create(
                            lokale_overheid=catalog.lokale_overheid,
                            organisatie=catalog.lokale_overheid.organisatie,
                        )

                    # If it doesn't exist yet, create a (specific) product in
                    # this (specific) catalog.
                    product, is_created = Product.objects.get_or_create(
                        referentie_product=reference_product,
                        catalogus=catalog,
                        defaults={
                            "generiek_product": reference_product.generiek_product,
                            "bevoegde_organisatie": default_auth_org,
                        },
                    )

                    # Make sure the product has an authorized organisation.
                    if not is_created and product.bevoegde_organisatie is None:
                        Product.objects.filter(pk=product.pk).update(
                            bevoegde_organisatie=default_auth_org
                        )
                        corrections.append("added missing authorized organisation")

                    # For newly created products, create an initial version.
                    if is_created or product.versies.count() == 0:
                        created_products += 1
                        product_version = ProductVersie.objects.create(
                            product=product,
                            publicatie_datum=None,
                        )
                        # If the product was not created but there were no
                        # active versions, report this as a correction.
                        if not is_created:
                            corrections.append("added initial version")
                    else:
                        # Since we're also scanning to make corrections, we grab
                        # the most recent product version here to check its
                        # translations.
                        product_version = product.most_recent_version

                    if is_created or product_version.vertalingen.count() != len(
                        TaalChoices.values.keys()
                    ):
                        if not is_created:
                            corrections.append("added missing translations")

                        # Create localized product version based on available
                        # languages.
                        for language in TaalChoices.labels.keys():
                            localized_product_version = LocalizedProduct.objects.create(
                                product_versie=product_version,
                                taal=language,
                            )
                            # Copy the reference texts
                            if active_reference_product_version:
                                localized_reference_product_version = (
                                    active_reference_product_version.vertalingen.filter(
                                        taal=language
                                    ).first()
                                )
                                if localized_reference_product_version:
                                    localized_product_version.update_with_reference_texts(
                                        localized_reference_product_version
                                    )

                    elif _fill_empty_english_text:
                        corrections.append(
                            "updated only empty english text with reference texts"
                        )
                        product_version.update_with_reference_texts(
                            active_reference_product_version,
                            languages=[TaalChoices.en],
                            skip_filled_fields=True,
                        )

                    # Update products with the latest reference texts if there
                    # is a reference text and the product hasn't been touched
                    # yet, ever.
                    elif (
                        active_reference_product_version
                        and active_reference_product_version.gewijzigd_op
                        > product_version.gewijzigd_op
                        and product_version.versie == 1
                        and product_version.publicatie_datum is None
                        and product_version.gewijzigd_op - product_version.gemaakt_op
                        < datetime.timedelta(minutes=1)
                    ):
                        corrections.append("updated with latest reference texts")
                        product_version.update_with_reference_texts(
                            active_reference_product_version
                        )

                    current_count += 1
                    if corrections:
                        correction_msg = ", ".join(corrections)
                        self.stdout.write(
                            f"[{perc(current_count)}] Corrected product '{product}' ({product.pk}) in catalog '{catalog}' for '{catalog.lokale_overheid}': {correction_msg}"
                        )
                    elif is_created:
                        self.stdout.write(
                            f"[{perc(current_count)}] Created new product '{product}' ({product.pk}) in catalog '{catalog}' for '{catalog.lokale_overheid}'."
                        )

        self.stdout.write(f"Created {created_catalogs} catalogs.")
        self.stdout.write(f"Created {created_products} products.")

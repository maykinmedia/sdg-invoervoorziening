from datetime import date
import datetime
from django.test import TestCase, TransactionTestCase
from django.core.management import call_command

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory
from sdg.producten.models.localized import LocalizedProduct
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductFactory,
)

from sdg.core.models import ProductenCatalogus
from sdg.producten.models.product import Product, ProductVersie


class UpdateCatalogTests(TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.producten_catalogus_database = ProductenCatalogus.objects.all()
        self.producten_database = Product.objects.all()
        self.producten_versies_database = ProductVersie.objects.all()
        self.localized_producten_database = LocalizedProduct.objects.all()

    def test_create_catalog_from_reference_if_enabled(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(self.producten_catalogus_database.count(), 1)
        call_command("update_catalogs")
        self.assertNotEqual(self.producten_catalogus_database.count(), 1)

    def test_no_create_catalog_from_reference_if_disabled(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(self.producten_catalogus_database.count(), 1)
        call_command("update_catalogs")
        self.assertEqual(self.producten_catalogus_database.count(), 1)

    def test_create_products_from_reference_product(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(catalogus=ref_catalog)
        ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(self.producten_database.count(), 1)
        call_command("update_catalogs")
        self.assertEqual(self.producten_database.count(), 2)
        self.assertEqual(
            ref_product,
            self.producten_database.last().referentie_product,
        )

    def test_no_create_products_from_reference_without_active_version(self):
        # if product has no publicatie date check if we don't generate any products ?
        pass

    def test_correct_products_if_no_initial_version(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(catalogus=ref_catalog)

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(self.producten_database.count(), 1)
        call_command("update_catalogs")
        self.assertEqual(self.producten_database.count(), 2)
        self.assertEqual(
            self.producten_versies_database.last().product.referentie_product,
            ref_product,
        )

    def test_correct_products_if_no_translations(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(
            catalogus=ref_catalog,
        )
        ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(self.localized_producten_database.count(), 0)
        call_command("update_catalogs")
        self.assertEqual(self.localized_producten_database.count(), 2)
        self.assertEqual(self.localized_producten_database.first().taal, "nl")
        self.assertEqual(self.localized_producten_database.last().taal, "en")

    def test_update_products_with_latest_reference_texts(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(
            catalogus=ref_catalog,
        )
        ref_product_versie = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=1,
        )
        ref_localized_product_nl = LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        call_command("update_catalogs")

        generated_localized_product = (
            self.localized_producten_database.filter(taal="nl")
            .exclude(pk=ref_localized_product_nl.pk)
            .first()
        )

        # update referentie product versie and localized product
        self.producten_versies_database.filter(pk=ref_product_versie.pk).update(
            versie=2,
            gewijzigd_op=ref_product_versie.gemaakt_op + datetime.timedelta(days=1),
        )
        self.localized_producten_database.filter(pk=ref_localized_product_nl.pk).update(
            product_titel_decentraal="Lorem Ipsum",
            specifieke_tekst="Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
        )

        call_command("update_catalogs")
        self.assertEqual(
            self.localized_producten_database.get(
                pk=ref_localized_product_nl.pk
            ).product_titel_decentraal,
            self.localized_producten_database.get(
                pk=generated_localized_product.pk
            ).product_titel_decentraal,
        )

        self.assertEqual(
            self.localized_producten_database.get(
                pk=ref_localized_product_nl.pk
            ).specifieke_tekst,
            self.localized_producten_database.get(
                pk=generated_localized_product.pk
            ).specifieke_tekst,
        )

    def test_no_update_products_if_changed_to_latest_reference_texts(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(
            catalogus=ref_catalog,
        )
        ref_product_versie = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=1,
        )
        ref_localized_product_nl = LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        call_command("update_catalogs")

        generated_product_versie = self.producten_versies_database.exclude(
            pk=ref_product_versie.pk
        ).last()

        generated_localized_product = (
            self.localized_producten_database.filter(taal="nl")
            .exclude(pk=ref_localized_product_nl.pk)
            .first()
        )

        # update referentie product versie and localized product
        self.producten_versies_database.filter(pk=ref_product_versie.pk).update(
            versie=2,
            gewijzigd_op=ref_product_versie.gemaakt_op + datetime.timedelta(days=1),
        )
        self.localized_producten_database.filter(pk=ref_localized_product_nl.pk).update(
            product_titel_decentraal="Lorem Ipsum",
            specifieke_tekst="Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
        )

        # update newly generated product versie and localized product
        self.producten_versies_database.filter(pk=generated_product_versie.pk).update(
            versie=3,
            gewijzigd_op=generated_product_versie.gemaakt_op
            + datetime.timedelta(days=2),
        )
        self.localized_producten_database.filter(
            pk=generated_localized_product.pk
        ).update(
            product_titel_decentraal="Updated Product title decentraal",
            specifieke_tekst="Updated Specifieke tekst.",
        )

        call_command("update_catalogs")

        self.assertNotEqual(
            self.localized_producten_database.get(
                pk=ref_localized_product_nl.pk
            ).product_titel_decentraal,
            self.localized_producten_database.get(
                pk=generated_localized_product.pk
            ).product_titel_decentraal,
        )

        self.assertNotEqual(
            self.localized_producten_database.get(
                pk=ref_localized_product_nl.pk
            ).specifieke_tekst,
            self.localized_producten_database.get(
                pk=generated_localized_product.pk
            ).specifieke_tekst,
        )

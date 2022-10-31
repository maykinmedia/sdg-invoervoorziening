from datetime import date, timedelta

from django.core.management import call_command
from django.db.models import Q
from django.test import TestCase

from sdg.core.models import ProductenCatalogus
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory
from sdg.producten.models.localized import LocalizedProduct
from sdg.producten.models.product import Product, ProductVersie
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductFactory,
)


class UpdateCatalogTests(TestCase):
    def test_create_catalog_from_reference_if_enabled(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_producten_catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )

        locale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(ProductenCatalogus.objects.all().count(), 1)
        call_command("update_catalogs")
        self.assertEqual(ProductenCatalogus.objects.all().count(), 2)

        new_catalog = ProductenCatalogus.objects.get(
            is_referentie_catalogus=False
        )  # There's only 1 in this test

        self.assertEqual(new_catalog.lokale_overheid, locale_overheid)
        self.assertEqual(new_catalog.versie, ref_producten_catalogus.versie)
        self.assertEqual(
            new_catalog.naam, f"{locale_overheid} ({ref_producten_catalogus.naam})"
        )

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

        self.assertEqual(ProductenCatalogus.objects.all().count(), 1)
        call_command("update_catalogs")
        self.assertEqual(ProductenCatalogus.objects.all().count(), 1)

    def test_create_products_from_reference_product(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(catalogus=ref_catalog)
        ref_product_versie = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
        )
        ref_localized_product_nl = LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
        )

        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(Product.objects.all().count(), 1)

        call_command("update_catalogs")

        new_product = Product.objects.get(referentie_product=ref_product)
        new_product_versie = ProductVersie.objects.get(product=new_product)
        new_localized_product_nl = LocalizedProduct.objects.get(
            product_versie=new_product_versie, taal="nl"
        )

        self.assertEqual(Product.objects.all().count(), 2)
        self.assertEqual(new_product.catalogus.lokale_overheid, lokale_overheid)
        self.assertEqual(
            ref_localized_product_nl.specifieke_tekst,
            new_localized_product_nl.specifieke_tekst,
        )

    def test_correct_products_if_no_initial_version(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ref_product = ReferentieProductFactory.create(catalogus=ref_catalog)

        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(Product.objects.all().count(), 1)
        call_command("update_catalogs")
        new_product = Product.objects.get(referentie_product=ref_product)

        self.assertEqual(Product.objects.all().count(), 2)
        self.assertEqual(new_product.catalogus.lokale_overheid, lokale_overheid)

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

        self.assertEqual(LocalizedProduct.objects.all().count(), 0)
        call_command("update_catalogs")
        self.assertEqual(LocalizedProduct.objects.all().count(), 2)
        self.assertTrue(LocalizedProduct.objects.get(taal="nl"))
        self.assertTrue(LocalizedProduct.objects.get(taal="en"))

    def test_update_products_from_active_orgs_only(self):
        ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
        )
        ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=ref_overheid,
            is_referentie_catalogus=True,
        )
        ReferentieProductFactory.create(
            catalogus=ref_catalog,
        )

        inactive_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=date.today() - timedelta(days=1),
        )

        active_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        self.assertEqual(ProductenCatalogus.objects.all().count(), 1)

        call_command("update_catalogs")

        self.assertEqual(ProductenCatalogus.objects.all().count(), 2)
        self.assertTrue(
            ProductenCatalogus.objects.get(lokale_overheid=active_lokale_overheid)
        )
        self.assertTrue(
            ProductVersie.objects.get(
                product__catalogus__lokale_overheid=active_lokale_overheid
            )
        )

        self.assertFalse(
            ProductenCatalogus.objects.filter(lokale_overheid=inactive_lokale_overheid)
        )
        self.assertFalse(
            ProductVersie.objects.filter(
                product__catalogus__lokale_overheid=inactive_lokale_overheid
            )
        )

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
            publicatie_datum=date.today() - timedelta(days=1),
            versie=1,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
            product_titel_decentraal="Original title",
            specifieke_tekst="Original text",
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        call_command("update_catalogs")

        generated_product = Product.objects.get(~Q(pk=ref_product.pk))
        generated_product_versie = ProductVersie.objects.get(product=generated_product)
        generated_localized_product = LocalizedProduct.objects.get(
            taal="nl", product_versie=generated_product_versie
        )

        self.assertEqual(
            generated_localized_product.product_titel_decentraal,
            "Original title",
        )
        self.assertEqual(generated_localized_product.specifieke_tekst, "Original text")

        ref_product_versie_2 = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=2,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="nl",
            product_titel_decentraal="Updated title",
            specifieke_tekst="Updated text",
        )

        call_command("update_catalogs")
        generated_updated_localized_product = LocalizedProduct.objects.get(
            taal="nl", product_versie=generated_product_versie
        )

        self.assertEqual(
            generated_updated_localized_product.product_titel_decentraal,
            "Updated title",
        )
        self.assertEqual(
            generated_updated_localized_product.specifieke_tekst, "Updated text"
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
            publicatie_datum=date.today() - timedelta(days=1),
            versie=1,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
            product_titel_decentraal="Original title",
            specifieke_tekst="Original text",
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        call_command("update_catalogs")

        generated_product = Product.objects.get(~Q(pk=ref_product.pk))
        generated_product_versie = ProductVersie.objects.get(product=generated_product)
        generated_localized_product = LocalizedProduct.objects.get(
            taal="nl", product_versie=generated_product_versie
        )

        self.assertEqual(
            generated_localized_product.product_titel_decentraal,
            "Original title",
        )
        self.assertEqual(generated_localized_product.specifieke_tekst, "Original text")

        # new reference product version and localized product
        ref_product_versie_2 = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=2,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="nl",
            product_titel_decentraal="Updated reference title",
            specifieke_tekst="Updated reference text",
        )

        # Simulate publishing the generated product versie and localized data
        generated_product_versie.gewijzigd_op = date.today() + timedelta(days=1)
        generated_product_versie.publicatie_datum = date.today() + timedelta(days=1)
        generated_product_versie.save()

        generated_localized_product.product_titel_decentraal = "Changed by user title"
        generated_localized_product.specifieke_tekst = "Changed by user text"
        generated_localized_product.save()

        call_command("update_catalogs")
        generated_updated_localized_product = LocalizedProduct.objects.get(
            taal="nl", product_versie=generated_product_versie
        )

        self.assertEqual(
            generated_updated_localized_product.product_titel_decentraal,
            "Changed by user title",
        )
        self.assertEqual(
            generated_updated_localized_product.specifieke_tekst,
            "Changed by user text",
        )

    def test_update_catalogs_with_fill_empty_english_text(self):
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
            publicatie_datum=date.today() - timedelta(days=1),
            versie=1,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie,
            taal="nl",
            product_titel_decentraal="Original title",
            specifieke_tekst="Original text",
        )

        LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True,
            organisatie__owms_end_date=None,
        )

        call_command("update_catalogs")

        generated_product = Product.objects.get(~Q(pk=ref_product.pk))
        generated_product_versie = ProductVersie.objects.get(product=generated_product)
        generated_localized_product = LocalizedProduct.objects.get(
            taal="nl", product_versie=generated_product_versie
        )
        self.assertEqual(
            generated_localized_product.product_titel_decentraal,
            "Original title",
        )
        self.assertEqual(generated_localized_product.specifieke_tekst, "Original text")

        # Simulate user creating new product version
        product_versie_2 = ProductVersieFactory.create(
            product=generated_product,
            publicatie_datum=date.today(),
            versie=2,
        )
        localized_product_nl_2 = LocalizedProductFactory.create(
            taal="nl",
            product_versie=product_versie_2,
            product_titel_decentraal="titel NL",
            specifieke_tekst="",
            procedure_beschrijving="procedure beschrijving NL",
        )
        localized_product_en_2 = LocalizedProductFactory.create(
            taal="en",
            product_versie=product_versie_2,
            product_titel_decentraal="",
            specifieke_tekst="",
            procedure_beschrijving="Test description EN",
        )

        # Simulate localized reference product being updated
        ref_product_versie_2 = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=2,
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="nl",
            product_titel_decentraal="Updated title NL",
            specifieke_tekst="Updated text NL",
            procedure_beschrijving="Updated procedure description NL",
        )
        LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="en",
            product_titel_decentraal="Updated title EN",
            specifieke_tekst="Updated text EN",
            procedure_beschrijving="Updated procedure description EN",
        )

        call_command("update_catalogs", fill_empty_english_text=True)
        localized_product_en_2.refresh_from_db()

        self.assertEqual(
            localized_product_nl_2.product_titel_decentraal,
            "titel NL",
        )
        self.assertEqual(
            localized_product_nl_2.specifieke_tekst,
            "",
        )
        self.assertEqual(
            localized_product_nl_2.procedure_beschrijving,
            "procedure beschrijving NL",
        )
        self.assertEqual(
            localized_product_en_2.product_titel_decentraal,
            "Updated title EN",
        )
        self.assertEqual(
            localized_product_en_2.specifieke_tekst,
            "Updated text EN",
        )
        self.assertEqual(
            localized_product_en_2.procedure_beschrijving,
            "Test description EN",
        )

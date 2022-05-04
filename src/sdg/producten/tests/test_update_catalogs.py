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
        producten_catalogus_table = ProductenCatalogus.objects.all()

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

        self.assertEqual(producten_catalogus_table.count(), 1)
        call_command("update_catalogs")
        self.assertEqual(producten_catalogus_table.count(), 2)

    def test_no_create_catalog_from_reference_if_disabled(self):
        producten_catalogus_table = ProductenCatalogus.objects.all()

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

        self.assertEqual(producten_catalogus_table.count(), 1)
        call_command("update_catalogs")
        self.assertEqual(producten_catalogus_table.count(), 1)

    def test_create_products_from_reference_product(self):
        producten_table = Product.objects.all()
        producten_versies_table = ProductVersie.objects.all()
        localized_producten_table = LocalizedProduct.objects.all()

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

        self.assertEqual(producten_table.count(), 1)

        call_command("update_catalogs")

        new_product = producten_table.get(referentie_product=ref_product)
        new_product_versie = producten_versies_table.get(product=new_product)
        new_localized_product_nl = localized_producten_table.get(
            product_versie=new_product_versie, taal="nl"
        )

        self.assertEqual(producten_table.count(), 2)
        self.assertEqual(new_product.catalogus.lokale_overheid, lokale_overheid)
        self.assertEqual(
            ref_localized_product_nl.specifieke_tekst,
            new_localized_product_nl.specifieke_tekst,
        )

    def test_no_create_products_from_reference_without_active_version(self):
        # if product has no publicatie date check if we don't generate any products ?
        pass

    def test_correct_products_if_no_initial_version(self):
        producten_table = Product.objects.all()

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

        self.assertEqual(producten_table.count(), 1)
        call_command("update_catalogs")
        new_product = producten_table.get(referentie_product=ref_product)

        self.assertEqual(producten_table.count(), 2)
        self.assertEqual(new_product.catalogus.lokale_overheid, lokale_overheid)

    def test_correct_products_if_no_translations(self):
        localized_producten_table = LocalizedProduct.objects.all()

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

        self.assertEqual(localized_producten_table.count(), 0)
        call_command("update_catalogs")
        self.assertEqual(localized_producten_table.count(), 2)
        self.assertEqual(localized_producten_table.first().taal, "nl")
        self.assertEqual(localized_producten_table.last().taal, "en")

    def test_update_products_with_latest_reference_texts(self):
        producten_table = Product.objects.all()
        producten_versies_table = ProductVersie.objects.all()
        localized_producten_table = LocalizedProduct.objects.all()

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

        generated_product = producten_table.get(~Q(pk=ref_product.pk))
        generated_product_versie = producten_versies_table.get(
            product=generated_product
        )
        generated_localized_product = localized_producten_table.get(
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
        ref_updated_localized_product_nl = LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="nl",
            product_titel_decentraal="Updated title",
            specifieke_tekst="Updated text",
        )

        call_command("update_catalogs")
        generated_updated_localized_product = (
            localized_producten_table.filter(
                taal="nl", product_versie=generated_product_versie
            )
            .exclude(pk=ref_updated_localized_product_nl.pk)
            .first()
        )

        self.assertEqual(
            generated_updated_localized_product.product_titel_decentraal,
            "Updated title",
        )
        self.assertEqual(
            generated_updated_localized_product.specifieke_tekst, "Updated text"
        )

    def test_no_update_products_if_changed_to_latest_reference_texts(self):
        producten_table = Product.objects.all()
        producten_versies_table = ProductVersie.objects.all()
        localized_producten_table = LocalizedProduct.objects.all()

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

        generated_product = producten_table.get(~Q(pk=ref_product.pk))
        generated_product_versie = producten_versies_table.filter(
            product=generated_product
        )
        generated_localized_product = localized_producten_table.filter(
            taal="nl", product_versie=generated_product_versie.first()
        )

        self.assertEqual(
            generated_localized_product.first().product_titel_decentraal,
            "Original title",
        )
        self.assertEqual(
            generated_localized_product.first().specifieke_tekst, "Original text"
        )

        # new reference product version and localized product
        ref_product_versie_2 = ProductVersieFactory.create(
            product=ref_product,
            publicatie_datum=date.today(),
            versie=2,
        )
        ref_updated_localized_product_nl = LocalizedProductFactory.create(
            product_versie=ref_product_versie_2,
            taal="nl",
            product_titel_decentraal="Updated reference title",
            specifieke_tekst="Updated reference text",
        )

        # new generated product version and localized product
        generated_product_versie.update(
            gewijzigd_op=date.today() + timedelta(days=1),
            publicatie_datum=date.today() + timedelta(days=1),
        )
        generated_localized_product.update(
            product_titel_decentraal="Updated generated title",
            specifieke_tekst="Updated generated text",
        )

        call_command("update_catalogs")
        generated_updated_localized_product = (
            localized_producten_table.filter(
                taal="nl", product_versie=generated_product_versie.first()
            )
            .exclude(pk=ref_updated_localized_product_nl.pk)
            .first()
        )

        self.assertEqual(
            generated_updated_localized_product.product_titel_decentraal,
            "Updated generated title",
        )
        self.assertEqual(
            generated_updated_localized_product.specifieke_tekst,
            "Updated generated text",
        )

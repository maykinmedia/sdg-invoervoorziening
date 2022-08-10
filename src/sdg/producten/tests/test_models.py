from django.core.exceptions import ValidationError
from django.test import TestCase

from freezegun import freeze_time

from sdg.core.constants.product import ProductStatus
from sdg.core.tests.factories.logius import UniformeProductnaamFactory
from sdg.producten.tests.constants import FUTURE_DATE, NOW_DATE
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedReferentieProductFactory,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductVersieFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductFactory,
    SpecifiekProductVersieFactory,
)


class GeneriekProductTest(TestCase):
    def test_is_sdg_product_property(self):
        sdg_upn = UniformeProductnaamFactory.create(sdg=["D1"])
        sdg_product = GeneriekProductFactory.create(upn=sdg_upn)
        self.assertTrue(sdg_product.is_sdg_product)

        upn = UniformeProductnaamFactory.create(sdg=[])
        product = GeneriekProductFactory.create(upn=upn)
        self.assertFalse(product.is_sdg_product)

    def test_product_status_property_new(self):
        new_upn = UniformeProductnaamFactory.create(is_verwijderd=False)
        new_generic_product = GeneriekProductFactory.create(
            upn=new_upn,
            eind_datum=None,
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=new_generic_product,
            product_titel="",
            generieke_tekst="",
            korte_omschrijving="",
            datum_check=None,
            verwijzing_links=[],
            landelijke_link="",
            size=2,
        )
        ReferentieProductVersieFactory.create(
            product__generiek_product=new_generic_product,
        )

        self.assertEqual(new_generic_product.product_status, ProductStatus.labels.NEW)

    def test_product_status_property_monitor(self):
        new_upn = UniformeProductnaamFactory.create(is_verwijderd=False)
        new_generic_product = GeneriekProductFactory.create(
            upn=new_upn,
            eind_datum=None,
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=new_generic_product,
            product_titel="test",
            generieke_tekst="test",
            korte_omschrijving="test",
            datum_check=None,
            verwijzing_links=[],
            landelijke_link="https://test.nl",
            size=2,
        )
        new_product_versie = ReferentieProductVersieFactory.create(
            product__generiek_product=new_generic_product,
        )
        LocalizedReferentieProductFactory.create_batch(
            product_versie=new_product_versie,
            product_titel_decentraal="",
            specifieke_tekst="",
            verwijzing_links=[],
            procedure_beschrijving="",
            vereisten="",
            bewijs="",
            bezwaar_en_beroep="",
            kosten_en_betaalmethoden="",
            uiterste_termijn="",
            wtd_bij_geen_reactie="",
            decentrale_procedure_link="",
            product_valt_onder_toelichting="",
            product_aanwezig_toelichting="",
            size=2,
        )

        self.assertEqual(
            new_generic_product.product_status, ProductStatus.labels.MONITOR
        )

    def test_product_status_property_publicate(self):
        new_upn = UniformeProductnaamFactory.create(is_verwijderd=False)
        new_generic_product = GeneriekProductFactory.create(
            upn=new_upn,
            eind_datum=None,
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=new_generic_product,
            product_titel="test",
            generieke_tekst="test",
            korte_omschrijving="test",
            datum_check=None,
            verwijzing_links=[],
            landelijke_link="https://test.nl",
            size=2,
        )
        new_product_versie = ReferentieProductVersieFactory.create(
            product__generiek_product=new_generic_product,
        )
        LocalizedReferentieProductFactory.create_batch(
            product_versie=new_product_versie,
            product_titel_decentraal="test",
            specifieke_tekst="test",
            verwijzing_links=[],
            procedure_beschrijving="test",
            vereisten="test",
            bewijs="test",
            bezwaar_en_beroep="test",
            kosten_en_betaalmethoden="test",
            uiterste_termijn="test",
            wtd_bij_geen_reactie="test",
            decentrale_procedure_link="https://www.test.nl",
            product_valt_onder_toelichting="test",
            product_aanwezig_toelichting="test",
            size=2,
        )

        self.assertEqual(
            new_generic_product.product_status, ProductStatus.labels.MONITOR
        )

    def test_product_status_property_missing(self):
        new_upn = UniformeProductnaamFactory.create(is_verwijderd=False)
        new_generic_product = GeneriekProductFactory.create(
            upn=new_upn,
            eind_datum=None,
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=new_generic_product,
            product_titel="test",
            generieke_tekst="test",
            korte_omschrijving="test",
            datum_check=None,
            verwijzing_links=[],
            landelijke_link="https://test.nl",
            size=2,
        )

        self.assertEqual(
            new_generic_product.product_status, ProductStatus.labels.MISSING
        )

    def test_product_status_property_expired(self):
        vervallen_upn = UniformeProductnaamFactory.create(is_verwijderd=True)
        vervallen_generic_product = GeneriekProductFactory.create(
            upn=vervallen_upn, eind_datum=None
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=vervallen_generic_product, size=2
        )
        ReferentieProductVersieFactory.create(
            product__generiek_product=vervallen_generic_product
        )

        self.assertEqual(
            vervallen_generic_product.product_status, ProductStatus.labels.EXPIRED
        )

    def test_product_status_property_end_of_life(self):
        vervallen_upn = UniformeProductnaamFactory.create()
        vervallen_generic_product = GeneriekProductFactory.create(
            upn=vervallen_upn,
            eind_datum=FUTURE_DATE,
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=vervallen_generic_product, size=2
        )
        ReferentieProductVersieFactory.create(
            product__generiek_product=vervallen_generic_product
        )

        self.assertEqual(
            vervallen_generic_product.product_status, ProductStatus.labels.EOL
        )

    def test_product_status_property_deleted(self):
        vervallen_upn = UniformeProductnaamFactory.create()
        vervallen_generic_product = GeneriekProductFactory.create(
            upn=vervallen_upn, eind_datum=NOW_DATE
        )
        LocalizedGeneriekProductFactory.create_batch(
            generiek_product=vervallen_generic_product, size=2
        )
        ReferentieProductVersieFactory.create(
            product__generiek_product=vervallen_generic_product
        )

        self.assertEqual(
            vervallen_generic_product.product_status, ProductStatus.labels.DELETED
        )


class ProductTests(TestCase):
    @freeze_time(NOW_DATE)
    def test_most_recent_version(self):
        product = SpecifiekProductFactory.create()
        *_, v3 = ProductVersieFactory.create_batch(
            3,
            product=product,
            publicatie_datum=NOW_DATE,
        )
        self.assertEqual(product.most_recent_version, v3)

    @freeze_time(NOW_DATE)
    def test_most_recent_version_can_be_concept(self):
        product = SpecifiekProductFactory.create()
        version = ProductVersieFactory.create(product=product, publicatie_datum=None)
        self.assertEqual(product.most_recent_version, version)

    @freeze_time(NOW_DATE)
    def test_most_recent_version_with_multiple_products(self):
        p1, p2, p3 = SpecifiekProductVersieFactory.create_batch(3)
        self.assertEqual(p1.product.most_recent_version, p1)
        self.assertEqual(p2.product.most_recent_version, p2)
        self.assertEqual(p3.product.most_recent_version, p3)

    @freeze_time(NOW_DATE)
    def test_active_version(self):
        product = SpecifiekProductFactory.create()
        ProductVersieFactory.create(product=product, publicatie_datum=None)
        active = ProductVersieFactory.create(product=product, publicatie_datum=NOW_DATE)
        ProductVersieFactory.create(product=product, publicatie_datum=FUTURE_DATE)
        self.assertEqual(product.active_version, active)

    @freeze_time(NOW_DATE)
    def test_active_version_with_multiple_products(self):
        p1, p2, p3 = SpecifiekProductVersieFactory.create_batch(
            3, publicatie_datum=NOW_DATE
        )
        self.assertEqual(p1.product.active_version, p1)
        self.assertEqual(p2.product.active_version, p2)
        self.assertEqual(p3.product.active_version, p3)


class LabeledURLTests(TestCase):
    def setUp(self):
        super().setUp()

        self.localized_product = LocalizedReferentieProductFactory.create()

    def test_able_to_save_labeled_urls(self):
        self.localized_product.verwijzing_links = [
            ["label1", "https://example.com"],
            ["label2", "https://example2.com"],
            ["label3", "https://example3.com"],
        ]
        self.localized_product.full_clean()

    def test_unable_to_save_labeled_urls_without_label(self):
        with self.assertRaises(ValidationError):
            self.localized_product.verwijzing_links = [
                ["label1", "https://example.com"],
                ["label2", "https://example2.com"],
                ["", "https://example2.com"],
            ]
            self.localized_product.full_clean()

    def test_unable_to_save_labeled_urls_with_invalid_url(self):
        with self.assertRaises(ValidationError):
            self.localized_product.verwijzing_links = [
                ["label1", "examplecom"],
            ]
            self.localized_product.full_clean()

    def test_unable_to_save_labeled_urls_with_extra_items(self):
        with self.assertRaises(ValidationError):
            self.localized_product.verwijzing_links = [
                ["label1", "https://example.com", "extra1"],
            ]
            self.localized_product.full_clean()

    def test_unable_to_save_markdown_with_invaled_h_elements(self):
        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "# example text."

            self.localized_product.full_clean()

        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "## example text."

            self.localized_product.full_clean()

        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "##### example text."

            self.localized_product.full_clean()

        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "###### example text."

            self.localized_product.full_clean()

    def test_unable_to_save_markdown_with_img_element(self):
        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = (
                "![alt](/path/to/image.jpg 'title') example text."
            )

            self.localized_product.full_clean()

    def test_unable_to_save_markdown_with_hr_element(self):
        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "___"

            self.localized_product.full_clean()

        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "---"

            self.localized_product.full_clean()

        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "***"

            self.localized_product.full_clean()

    def test_unable_to_save_markdown_with_code_element(self):
        with self.assertRaises(ValidationError):
            self.localized_product.specifieke_tekst = "`example text` example text."

            self.localized_product.full_clean()

    def test_able_to_save_markdown(self):
        self.localized_product.specifieke_tekst = "### example text\n * example text\n * example text\n * example text\n 1. example text\n 2. example text\n 3. example text\n *italic* **bold**."

        self.localized_product.full_clean()

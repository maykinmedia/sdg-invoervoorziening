from django.core.exceptions import ValidationError
from django.test import TestCase

from freezegun import freeze_time

from sdg.producten.tests.constants import NOW_DATE
from sdg.producten.tests.factories.localized import LocalizedReferentieProductFactory
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    SpecifiekProductFactory,
    SpecifiekProductVersieFactory,
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
        v1, v2, v3 = SpecifiekProductVersieFactory.create_batch(3)
        self.assertEqual(v1.product.most_recent_version, v1)
        self.assertEqual(v2.product.most_recent_version, v2)
        self.assertEqual(v3.product.most_recent_version, v3)


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

from django.core.exceptions import ValidationError
from django.test import TestCase

from sdg.producten.tests.factories.localized import LocalizedReferentieProductFactory


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

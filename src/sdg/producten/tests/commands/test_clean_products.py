from django.core.management import call_command
from django.test import TestCase

from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedSpecifiekProductFactory,
)


class CleanProductsTests(TestCase):
    def test_clean_products_with_first_availability_explanation__dutch(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="nl")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="nl",
        )

        formatted_text = "De gemeente {lokale_overheid} levert het product {product} niet.".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_aanwezig_toelichting = formatted_text
        localized_product.product_versie.product.product_aanwezig = False
        localized_product.save()
        self.assertEqual(localized_product.product_aanwezig_toelichting, formatted_text)

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_aanwezig_toelichting, "")

    def test_clean_products_with_second_availability_explanation__dutch(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="nl")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="nl",
        )

        formatted_text = "De gemeente {lokale_overheid} levert het product {product} niet omdat...".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_aanwezig_toelichting = formatted_text
        localized_product.product_versie.product.product_aanwezig = False
        localized_product.save()
        self.assertEqual(localized_product.product_aanwezig_toelichting, formatted_text)

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_aanwezig_toelichting, "")

    def test_clean_products_with_first_availability_explanation__english(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="en")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="en",
        )

        formatted_text = "The municipality of {lokale_overheid} doesn't offer {product}.".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_aanwezig_toelichting = formatted_text
        localized_product.product_versie.product.product_aanwezig = False
        localized_product.save()
        self.assertEqual(localized_product.product_aanwezig_toelichting, formatted_text)

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_aanwezig_toelichting, "")

    def test_clean_products_with_second_availability_explanation__english(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="en")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="en",
        )

        formatted_text = "The municipality of {lokale_overheid} doesn't offer {product} because...".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_aanwezig_toelichting = formatted_text
        localized_product.product_versie.product.product_aanwezig = False
        localized_product.save()
        self.assertEqual(localized_product.product_aanwezig_toelichting, formatted_text)

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_aanwezig_toelichting, "")

    def test_clean_products_with_first_falls_under_explanation__dutch(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="nl")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="nl",
        )

        formatted_text = "In de gemeente {lokale_overheid} is {product} onderdeel van [product].".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_valt_onder_toelichting = formatted_text
        localized_product.save()
        self.assertEqual(
            localized_product.product_valt_onder_toelichting, formatted_text
        )

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_valt_onder_toelichting, "")

    def test_clean_products_with_first_falls_under_explanation__english(self):
        localized_product = LocalizedSpecifiekProductFactory.create(taal="en")
        generic_product = localized_product.product_versie.product.generiek_product
        localized_generic_product = LocalizedGeneriekProductFactory.create(
            generiek_product=generic_product,
            taal="en",
        )

        formatted_text = "In the municipality of {lokale_overheid}, {product} falls under [product].".format(
            lokale_overheid=localized_product.product_versie.product.catalogus.lokale_overheid,
            product=localized_generic_product,
        )
        localized_product.product_valt_onder_toelichting = formatted_text
        localized_product.save()
        self.assertEqual(
            localized_product.product_valt_onder_toelichting, formatted_text
        )

        call_command("clean_products")

        localized_product.refresh_from_db()
        self.assertEqual(localized_product.product_valt_onder_toelichting, "")

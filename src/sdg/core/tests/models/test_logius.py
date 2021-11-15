from django.test import TestCase

from sdg.core.models import UniformeProductnaam
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import UniformeProductnaamFactory


class TestUniformeProductnaam(TestCase):
    def test_save_upn_with_autofill_catalog(self):
        autofill_catalog = ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["SDG"],
            is_referentie_catalogus=True,
        )

        upn = UniformeProductnaamFactory.create(upn_label="UPN1 (SDG)")
        self.assertEqual(1, UniformeProductnaam.objects.count())
        self.assertEqual(1, autofill_catalog.producten.count())

        self.assertEqual(1, upn.generieke_producten.count())
        generic_product = upn.generieke_producten.get()
        self.assertEqual(2, generic_product.vertalingen.count())

        self.assertEqual(1, generic_product.producten.count())
        reference_product = generic_product.producten.get()

        self.assertEqual(1, reference_product.versies.count())
        reference_version = reference_product.versies.get()
        self.assertEqual(2, reference_version.vertalingen.count())

    def test_save_upn_without_autofill_catalog(self):
        autofill_catalog = ProductenCatalogusFactory.create(
            autofill=False,
            is_referentie_catalogus=True,
        )

        UniformeProductnaamFactory.create(upn_label="UPN1 (SDG)")
        self.assertEqual(1, UniformeProductnaam.objects.count())
        self.assertEqual(0, autofill_catalog.producten.count())

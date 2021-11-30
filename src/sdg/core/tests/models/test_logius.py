from django.test import TestCase

from sdg.core.models import UniformeProductnaam
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import UniformeProductnaamFactory


class TestUniformeProductnaam(TestCase):
    def test_get_active_fields(self):
        upn = UniformeProductnaamFactory.create(
            upn_label="UPN1", provincie=True, waterschap=True
        )
        self.assertEqual(upn.get_active_fields(), {"provincie", "waterschap"})

    def test_save_upn_with_autofill_catalog_generates_initial_data(self):
        autofill_catalog = ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["provincie", "waterschap"],
            is_referentie_catalogus=True,
        )

        upn = UniformeProductnaamFactory.create(
            upn_label="UPN1", provincie=True, waterschap=True
        )
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

    def test_save_upn_with_autofill_catalog_does_not_generate_initial_data_if_no_match(
        self,
    ):
        autofill_catalog = ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["provincie", "waterschap"],
            is_referentie_catalogus=True,
        )
        UniformeProductnaamFactory.create(
            upn_label="UPN1", provincie=True, waterschap=False
        )

        self.assertEqual(1, UniformeProductnaam.objects.count())
        self.assertEqual(0, autofill_catalog.producten.count())

    def test_save_upn_without_autofill_catalog_does_not_generate_initial_data(self):
        autofill_catalog = ProductenCatalogusFactory.create(
            autofill=False,
            is_referentie_catalogus=True,
        )

        UniformeProductnaamFactory.create(upn_label="UPN1")
        self.assertEqual(1, UniformeProductnaam.objects.count())
        self.assertEqual(0, autofill_catalog.producten.count())

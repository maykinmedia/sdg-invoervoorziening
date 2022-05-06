from unittest import skip

from django.test import TestCase

from sdg.core.utils import get_from_cache
from sdg.producten.models.managers import ProductQuerySet
from sdg.producten.tests.factories.product import SpecifiekProductFactory


class UtilsTests(TestCase):
    def test_get_from_cache(self):
        product = SpecifiekProductFactory.create()
        product.save()

        result = get_from_cache(
            product, "name", manager_methods=[ProductQuerySet.annotate_name]
        )

        self.assertNumQueries(2)
        self.assertEqual(result, product.generiek_product.upn.upn_label)

    @skip(
        "This test can no longer run since a product needs to be either a reference product, or a generic product"
    )
    def test_get_from_cache_none_value_recursion_error(self):
        """
        This test that cached properties correctly differentiate between no
        cached value and a cached value of None. Otherwise, an infinite loop
        occurs.
        """

        product = SpecifiekProductFactory.create()
        product.referentie_product = None
        product.generiek_product = None
        product.save()

        result = get_from_cache(
            product, "name", manager_methods=[ProductQuerySet.annotate_name]
        )

        self.assertNumQueries(2)
        self.assertIsNone(result)

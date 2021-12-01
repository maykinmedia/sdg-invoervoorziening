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

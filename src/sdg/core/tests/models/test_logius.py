from django.test import TestCase

from sdg.core.tests.factories.logius import UniformeProductnaamFactory


class TestUniformeProductnaam(TestCase):
    def test_get_active_fields(self):
        upn = UniformeProductnaamFactory.create(
            upn_label="UPN1", provincie=True, waterschap=True
        )
        self.assertEqual(upn.get_active_fields(), {"provincie", "waterschap"})

    def test_get_active_fields_with_sdg(self):
        upn = UniformeProductnaamFactory.create(
            upn_label="UPN1", provincie=True, waterschap=True, sdg=["A1", "B2"]
        )
        self.assertEqual(upn.get_active_fields(), {"provincie", "waterschap", "sdg"})

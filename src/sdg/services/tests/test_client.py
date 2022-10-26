from django.test import TestCase

from zgw_consumers.models import Service

from sdg.core.constants import DoelgroepChoices
from sdg.services.models import ServiceConfiguration


class SDGClientTests(TestCase):
    def test_build_client_without_schema(self):
        self.service = Service.objects.create(
            label="test",
            api_type="ztc",
            api_root="https://a-api.nederlandwereldwijd.nl/sdg/gt/v1/",
            auth_type="no_auth",
        )
        self.service_config = ServiceConfiguration.objects.create(
            service=self.service,
            doelgroep=DoelgroepChoices.burger,
        )
        client = self.service.build_client()
        self.assertIsNotNone(client.schema)
        self.assertEqual(
            client.base_url, "https://a-api.nederlandwereldwijd.nl/sdg/gt/v1/"
        )
        self.assertEqual(client.base_path, "/sdg/gt/v1/")
        self.assertEqual(client.products_url, "/sdg/gt/v1/producten")

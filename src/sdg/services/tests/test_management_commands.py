import json
import os
from unittest.mock import patch

from zgw_consumers.models import Service

from sdg.core.tests.test_management_commands import CommandTestCase
from sdg.producten.models import GeneriekProduct
from sdg.services.models import ServiceConfiguration

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestImportDataFromServices(CommandTestCase):
    def setUp(self):
        service = Service.objects.create(
            label="test",
            api_type="ztc",
            api_root="https://example.com/api/v2/",
            auth_type="no_auth",
            oas="https://example.com/api/v2/openapi.json",
        )
        ServiceConfiguration.objects.create(
            service=service,
            doelgroep="eu-burger",
        )

    @patch("sdg.services.models.ServiceConfiguration.retrieve_products")
    def test_import_data_from_services(self, retrieve_mock):
        with open(os.path.join(TESTS_DIR, "data/example_api_response.json")) as f:
            retrieve_mock.return_value = json.load(f)["results"]

        # out = self.call_command("import_data_from_services")
        # TODO
        self.assertEqual(20, GeneriekProduct.objects.count())

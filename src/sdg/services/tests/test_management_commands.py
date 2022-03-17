import json
import os
from datetime import datetime
from unittest.mock import patch

from zgw_consumers.models import Service

from sdg.core.constants import DoelgroepChoices
from sdg.core.tests.factories.logius import UniformeProductnaamFactory
from sdg.core.tests.test_management_commands import CommandTestCase
from sdg.producten.tests.factories.localized import LocalizedGeneriekProductFactory
from sdg.services.models import ServiceConfiguration

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestImportDataFromServices(CommandTestCase):
    def setUp(self):
        self.service = Service.objects.create(
            label="test",
            api_type="ztc",
            api_root="https://sdgapi.ondernemersplein.kvk.nl/api/v1/",
            auth_type="no_auth",
            oas="https://sdgapi.ondernemersplein.kvk.nl/swagger/v1/swagger.json",
        )
        self.service_config = ServiceConfiguration.objects.create(
            service=self.service,
            doelgroep=DoelgroepChoices.burger,
        )
        self.upn_1 = UniformeProductnaamFactory.create(
            upn_label="verklaring omtrent gedrag (vog)"
        )
        self.upn_2 = UniformeProductnaamFactory.create(upn_label="toeristenbelasting")
        self.localized_1 = LocalizedGeneriekProductFactory.create(
            generiek_product__upn=self.upn_1,
            taal="en",
            generiek_product__doelgroep=DoelgroepChoices.burger,
        )
        self.localized_2 = LocalizedGeneriekProductFactory.create(
            generiek_product__upn=self.upn_2,
            taal="en",
            generiek_product__doelgroep=DoelgroepChoices.burger,
        )

    @patch("sdg.services.models.ServiceConfiguration.retrieve_products")
    def test_import_data_from_services(self, retrieve_mock):
        with open(os.path.join(TESTS_DIR, "data/example_api_response.json")) as f:
            retrieve_mock.return_value = json.load(f)["results"]

        out = self.call_command("import_data_from_services")
        self.assertIn("Successfully updated 2 localized generic products.", out)

        self.localized_1.refresh_from_db()
        self.assertEqual(
            "Certificate of conduct for individuals (VOG NP)",
            self.localized_1.product_titel,
        )
        self.assertIn("## VOG denial", self.localized_1.generieke_tekst)
        self.assertEqual(
            [
                [
                    "Certificate of conduct (Justis)",
                    "https://www.justis.nl/en/products/certificate-of-conduct",
                ],
                ["VOG check tool (Justis, in Dutch)", "https://vogcheck.justis.nl/"],
                [
                    "Frequently asked questions certificate of conduct (Justis)",
                    "https://www.justis.nl/en/service-contact/frequently-asked-questions/certificate-of-conduct",
                ],
                [
                    "Certificate of conduct for legal entities (VOG RP)",
                    "https://business.gov.nl/regulation/vogrp/",
                ],
                [
                    "Applying for a permit or subsidy with eHerkenning",
                    "https://business.gov.nl/regulation/applying-for-a-permit-or-subsidy-with-eherkenning/",
                ],
                [
                    "Register for persons active in the childcare sector",
                    "https://business.gov.nl/regulation/register-for-persons-active-in-the-childcare-sector/",
                ],
                [
                    "Refusing certificate of conduct (VOG) based on police data",
                    "https://business.gov.nl/amendment/refusing-certificate-conduct-vog-based-police-data/",
                ],
            ],
            self.localized_1.verwijzing_links,
        )
        self.assertEqual(
            "https://business.gov.nl/regulation/vog/", self.localized_1.landelijke_link
        )
        self.assertEqual(datetime(2021, 7, 28, 16, 27, 2), self.localized_1.datum_check)

    @patch("zgw_consumers.client.ZGWClient.retrieve")
    def test_import_data_from_services_unreachable_api(self, retrieve_mock):
        retrieve_mock.side_effect = ConnectionError
        self.call_command("import_data_from_services")

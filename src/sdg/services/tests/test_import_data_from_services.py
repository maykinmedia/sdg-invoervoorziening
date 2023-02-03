import json
import os
from datetime import datetime
from unittest.mock import patch

from zgw_consumers.models import Service

from sdg.core.constants import DoelgroepChoices
from sdg.core.tests.factories.logius import (
    OverheidsorganisatieFactory,
    UniformeProductnaamFactory,
)
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
            upn_uri="http://standaarden.overheid.nl/owms/terms/geluidsontheffing"
        )
        self.upn_2 = UniformeProductnaamFactory.create(
            upn_uri="http://standaarden.overheid.nl/owms/terms/toeristenbelasting",
        )
        self.localized_1 = LocalizedGeneriekProductFactory.create(
            generiek_product__upn=self.upn_1,
            taal="nl",
            generiek_product__doelgroep=DoelgroepChoices.burger,
        )
        self.localized_2 = LocalizedGeneriekProductFactory.create(
            generiek_product__upn=self.upn_2,
            taal="nl",
            generiek_product__doelgroep=DoelgroepChoices.burger,
        )
        OverheidsorganisatieFactory.create(
            owms_pref_label="Rijksdienst voor Ondernemend Nederland",
            owms_identifier="http://standaarden.overheid.nl/owms/terms/RVO",
        )

    @patch("sdg.services.models.ServiceConfiguration.retrieve_products")
    def test_import_data_from_services(self, retrieve_mock):
        with open(os.path.join(TESTS_DIR, "data/example_api_response.json")) as f:
            retrieve_mock.return_value = json.load(f)["results"]

        out = self.call_command("import_data_from_services")
        self.assertIn("Successfully updated localized generic products.", out)

        self.localized_1.refresh_from_db()
        self.assertEqual(
            "Geluidsvoorschriften",
            self.localized_1.product_titel,
        )
        self.assertIn(
            "In sommige gemeenten moet u uw festiviteit een paar weken van",
            self.localized_1.generieke_tekst,
        )
        self.assertEqual(
            [
                [
                    "Regelgeving geluid (Kenniscentrum InfoMil)",
                    "http://www.infomil.nl/onderwerpen/geluid/regelgeving/",
                    "extern",
                ],
                [
                    "Akoestisch rapport (Kenniscentrum InfoMil)",
                    "http://www.infomil.nl/onderwerpen/geluid/thema/akoestisch-rapport-0/",
                    "extern",
                ],
                [
                    "Wet algemene bepalingen omgevingsrecht (Wabo) (Overheid.nl)",
                    "http://wetten.overheid.nl/1.0:c:BWBR0024779",
                    "wetgeving",
                ],
                [
                    "Wet geluidhinder (Wgh) (Overheid.nl)",
                    "http://wetten.overheid.nl/1.0:c:BWBR0003227",
                    "wetgeving",
                ],
                [
                    "Activiteitenbesluit milieubeheer (Barim) (Overheid.nl)",
                    "http://wetten.overheid.nl/1.0:c:BWBR0022762",
                    "wetgeving",
                ],
                [
                    "Activiteitenbesluit milieubeheer (Barim), Artikel 1.11. Akoestisch rapport (Overheid.nl)",
                    "http://wetten.overheid.nl/BWBR0022762/#Hoofdstuk1_Afdeling1.2_Artikel1.11",
                    "wetgeving",
                ],
                [
                    "Lokale wet- en regelgeving (Overheid.nl)",
                    "https://www.overheid.nl/lokale-wet-en-regelgeving",
                    "wetgeving",
                ],
            ],
            self.localized_1.verwijzing_links,
        )
        self.assertEqual(
            "https://ondernemersplein.kvk.nl/geluidsvoorschriften/",
            self.localized_1.landelijke_link,
        )
        self.assertEqual(
            datetime(2020, 11, 27, 15, 1, 59), self.localized_1.datum_check
        )
        self.assertEqual(
            self.localized_1.generiek_product.verantwoordelijke_organisaties.count(), 1
        )
        org = (
            self.localized_1.generiek_product.generiekproductoverheidsorganisatierol_set.all().first()
        )
        self.assertEqual(org.rol, "Ondersteuningsorganisatie")

    @patch("zgw_consumers.client.ZGWClient.retrieve")
    def test_import_data_from_services_unreachable_api(self, retrieve_mock):
        retrieve_mock.side_effect = ConnectionError
        self.call_command("import_data_from_services")

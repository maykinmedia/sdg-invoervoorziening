import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.logius import (
    OverheidsorganisatieFactory,
    UniformeProductnaamFactory,
)
from sdg.producten.tests.factories.localized import LocalizedGeneriekProductFactory
from sdg.producten.tests.factories.product import GeneriekProductFactory


class GeneriekeProductenTests(APITestCase):
    def setUp(self):
        self.overheidsorganisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.maykinmedia.nl",
            owms_pref_label="Maykin",
        )

        self.upn_1 = UniformeProductnaamFactory.create(
            upn_label="upn1",
            upn_uri="https://www.upn1.com",
            sdg=["C1, J1"],
            gemeente=True,
            provincie=True,
            waterschap=True,
        )
        self.generiek_product_burger = GeneriekProductFactory.create(
            upn=self.upn_1,
            doelgroep="eu-burger",
        )
        self.generiek_product_burger.verantwoordelijke_organisaties.add(
            self.overheidsorganisatie,
            through_defaults={"rol": "Ondersteuningsorganisatie"},
        )
        self.localized_gp_burger_1 = LocalizedGeneriekProductFactory.create(
            generiek_product=self.generiek_product_burger,
            taal="nl",
            product_titel="title",
            generieke_tekst="text",
            verwijzing_links=[
                ["label1", "http://www.example.com"],
                ["label2", "http://foobar.com"],
            ],
            landelijke_link="http://www.acme.com",
            laatst_gewijzigd=datetime.datetime(2022, 12, 10, 0, 0, 0),
            datum_check=datetime.datetime(2022, 12, 15, 0, 0, 0),
        )
        self.localized_gp_burger_1.verwijzing_links = [
            ["label1", "http://www.example.com", "category1"],
            ["label2", "http://foobar.com", "category2"],
        ]
        self.localized_gp_burger_1.save()

        self.localized_gp_burger_2 = LocalizedGeneriekProductFactory.create(
            generiek_product=self.generiek_product_burger,
            taal="en",
        )
        self.generiek_product_bedrijf = GeneriekProductFactory.create(
            upn=self.upn_1,
            doelgroep="eu-bedrijf",
        )
        (
            self.localized_gp_bedrijf_1,
            self.localized_gp_bedrijf_2,
        ) = LocalizedGeneriekProductFactory.create_batch(
            2,
            generiek_product=self.generiek_product_bedrijf,
        )

        self.upn_2 = UniformeProductnaamFactory.create(
            upn_label="upn2",
            upn_uri="https://www.upn2.com",
            sdg=["C1"],
            gemeente=True,
            provincie=True,
            waterschap=True,
        )
        self.generiek_product_burger_2 = GeneriekProductFactory.create(
            upn=self.upn_2,
            doelgroep="eu-burger",
        )
        (
            self.localized_gp_burger_3,
            self.localized_gp_burger_4,
        ) = LocalizedGeneriekProductFactory.create_batch(
            2,
            generiek_product=self.generiek_product_burger_2,
        )

        self.list_url = reverse("api:generic-product-list")

    def test_list_generieke_producten(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(6, len(data))

    def test_generieke_product_structure(self):
        # This will result in 1 product, the first we defined in self.setUp
        response = self.client.get(
            f"{self.list_url}?upnLabel={self.upn_1.upn_label}&doelgroep=eu-burger&taal=nl"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.json()["results"]))

        data = response.json()["results"][0]

        self.assertEqual(data["titel"], "title")
        self.assertEqual(data["tekst"], "text")
        self.assertEqual(len(data["links"]), 2)
        self.assertDictEqual(
            data["links"][0],
            {
                "label": "label1",
                "url": "http://www.example.com",
                "categorie": "category1",
            },
        )
        self.assertEqual(len(data["organisaties"]), 1)
        self.assertDictEqual(
            data["organisaties"][0],
            {
                "owmsPrefLabel": "Maykin",
                "owmsUri": "https://www.maykinmedia.nl",
                "rol": "Ondersteuningsorganisatie",
            },
        )
        self.assertEqual(data["laatstGecheckt"], "2022-12-15T00:00:00")
        self.assertEqual(data["laatstGewijzigd"], "2022-12-10T00:00:00")
        self.assertEqual(data["landelijkeLink"], "http://www.acme.com")
        self.assertEqual(data["upnUri"], "https://www.upn1.com")
        self.assertEqual(data["upnLabel"], "upn1")
        self.assertEqual(data["doelgroep"], "eu-burger")
        self.assertEqual(data["taal"], "nl")
        url = reverse(
            "api:generic-product-detail", args=[self.localized_gp_burger_1.uuid]
        )
        self.assertEqual(data["url"], f"http://testserver{url}")
        self.assertEqual(data["uuid"], self.localized_gp_burger_1.uuid)

    def test_retrieve_generiek_product_by_uuid(self):
        detail_url = reverse(
            "api:generic-product-detail", args=[self.localized_gp_burger_1.uuid]
        )

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(str(self.localized_gp_burger_1.uuid), data["uuid"])

    def test_filter_generieke_producten_by_upn_label(self):
        response = self.client.get(f"{self.list_url}?upnLabel={self.upn_1.upn_label}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(4, len(data))

    def test_filter_generieke_producten_by_upn_uri(self):
        response = self.client.get(f"{self.list_url}?upnUri={self.upn_2.upn_uri}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_filter_generieke_producten_by_doelgroep(self):
        response = self.client.get(f"{self.list_url}?doelgroep=eu-bedrijf")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_filter_generieke_producten_by_taal(self):
        response = self.client.get(f"{self.list_url}?taal=nl")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(3, len(data))

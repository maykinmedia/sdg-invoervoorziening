from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import (
    LokaleOverheidFactory,
    LokatieFactory,
)
from sdg.producten.tests.constants import FUTURE_DATE, NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.product import (
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
)


class ProductenCatalogusFilterTests(APITestCase):
    url = reverse("productencatalogus-list")

    def test_filter_organisatie(self):
        catalog, *_ = ProductenCatalogusFactory.create_batch(5)

        response = self.client.get(
            self.url, {"organisatie": f"{catalog.lokale_overheid.uuid}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(catalog.uuid), data[0]["uuid"])


class ProductFilterTests(APITestCase):
    url = reverse("product-list")

    def test_filter_organisatie(self):
        product, *_ = ReferentieProductFactory.create_batch(5)
        response = self.client.get(
            self.url, {"organisatie": str(product.catalogus.lokale_overheid.uuid)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(product.uuid), data[0]["uuid"])

    def test_filter_doelgroep(self):
        filter_string = "test_doelgroep"
        product = ReferentieProductFactory.create(
            doelgroep=["abc1", filter_string, "abc2"]
        )
        ReferentieProductFactory.create_batch(4)

        response = self.client.get(self.url, {"doelgroep": filter_string})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(product.uuid), data[0]["uuid"])

    def test_filter_catalogus(self):
        catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        product1, product2 = ReferentieProductFactory.create_batch(2, catalogus=catalog)
        ReferentieProductFactory.create_batch(3)

        response = self.client.get(self.url, {"catalogus": catalog.uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(2, len(data))
        self.assertEqual(str(product1.uuid), data[0]["uuid"])
        self.assertEqual(str(product2.uuid), data[1]["uuid"])

    @freeze_time(NOW_DATE)
    def test_filter_publicatie_datum(self):
        ReferentieProductVersieFactory.create(publicatie_datum=NOW_DATE)
        ReferentieProductVersieFactory.create_batch(2, publicatie_datum=FUTURE_DATE)
        ReferentieProductVersieFactory.create_batch(3, publicatie_datum=PAST_DATE)

        response = self.client.get(
            self.url, {"publicatieDatum": NOW_DATE.strftime("%Y-%m-%d")}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(3, len(data))


class LokatieFilterTests(APITestCase):
    url = reverse("lokatie-list")

    def test_filter_organisatie(self):
        location, *_ = LokatieFactory.create_batch(5)

        response = self.client.get(
            self.url, {"organisatie": f"{location.lokale_overheid.uuid}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(location.uuid), data[0]["uuid"])


class LokaleOverheidFilterTests(APITestCase):
    url = reverse("lokaleoverheid-list")

    def test_filter_organisatie(self):
        municipality, *_ = LokaleOverheidFactory.create_batch(5)

        response = self.client.get(
            self.url, {"owmsIdentifier": f"{municipality.organisatie.owms_identifier}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(municipality.uuid), data[0]["uuid"])

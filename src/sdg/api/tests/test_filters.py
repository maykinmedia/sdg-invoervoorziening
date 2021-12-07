from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.constants import TaalChoices
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import (
    LokaleOverheidFactory,
    LokatieFactory,
)
from sdg.producten.tests.constants import FUTURE_DATE, NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
)


class ProductenCatalogusFilterTests(APITestCase):
    url = reverse("api:productencatalogus-list")

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
    url = reverse("api:product-list")

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
        filter_string = "burgers"
        product = ReferentieProductFactory.create(doelgroep=[filter_string])
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

    def test_filter_upn_label(self):
        catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        product, *_ = ReferentieProductFactory.create_batch(5, catalogus=catalog)

        response = self.client.get(self.url, {"upnLabel": product.upn.upn_label})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(product.uuid), data[0]["uuid"])

    def test_filter_upn_uri(self):
        catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        product, *_ = ReferentieProductFactory.create_batch(5, catalogus=catalog)

        response = self.client.get(self.url, {"upnUri": product.upn.upn_uri})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(product.uuid), data[0]["uuid"])

    def test_filter_product_aanwezig(self):
        catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        ReferentieProductFactory.create_batch(
            3, catalogus=catalog, product_aanwezig=True
        )
        ReferentieProductFactory.create_batch(
            2, catalogus=catalog, product_aanwezig=False
        )
        ReferentieProductFactory.create_batch(
            1, catalogus=catalog, product_aanwezig=None
        )

        response = self.client.get(self.url, {"productAanwezig": "ja"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        self.assertEqual(3, len(data))

        response = self.client.get(self.url, {"productAanwezig": "nee"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        self.assertEqual(2, len(data))

        response = self.client.get(self.url, {"productAanwezig": "onbekend"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        self.assertEqual(1, len(data))

    @freeze_time(NOW_DATE)
    def test_filter_taal(self):
        catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )

        product1, product2, *_ = ReferentieProductFactory.create_batch(
            5, catalogus=catalog
        )

        product1_version = ProductVersieFactory.create(
            product=product1, publicatie_datum=PAST_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product1_version)

        product2_version = ProductVersieFactory.create(
            product=product2, publicatie_datum=PAST_DATE
        )
        LocalizedProductFactory.create(
            taal=TaalChoices.en, product_versie=product2_version
        )

        response = self.client.get(self.url, {"taal": "en"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        self.assertEqual(5, len(data))

        first_result, second_result, *_ = data

        self.assertEqual(1, len(first_result["vertalingen"]))
        self.assertEqual(1, len(second_result["vertalingen"]))

        self.assertEqual("en", first_result["vertalingen"][0]["taal"])
        self.assertEqual("en", second_result["vertalingen"][0]["taal"])

        response = self.client.get(self.url, {"taal": "nl"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        self.assertEqual(5, len(data))

        first_result, second_result, *_ = data

        self.assertEqual(1, len(first_result["vertalingen"]))
        self.assertEqual(0, len(second_result["vertalingen"]))

        self.assertEqual("nl", first_result["vertalingen"][0]["taal"])


class LokatieFilterTests(APITestCase):
    url = reverse("api:lokatie-list")

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
    url = reverse("api:lokaleoverheid-list")

    def test_filter_owms_identifier(self):
        municipality, *_ = LokaleOverheidFactory.create_batch(5)

        response = self.client.get(
            self.url, {"owmsIdentifier": f"{municipality.organisatie.owms_identifier}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(municipality.uuid), data[0]["uuid"])

    def test_filter_owms_pref_label(self):
        municipality, *_ = LokaleOverheidFactory.create_batch(5)

        response = self.client.get(
            self.url, {"owmsPrefLabel": f"{municipality.organisatie.owms_pref_label}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(1, len(data))
        self.assertEqual(str(municipality.uuid), data[0]["uuid"])

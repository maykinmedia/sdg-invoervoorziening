from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import BevoegdeOrganisatieFactory
from sdg.producten.tests.constants import NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
)


class ProductenTests(APITestCase):
    def test_list_products(self):
        ReferentieProductFactory.create_batch(2)
        list_url = reverse("api:product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_list_products_bevoegde_organisatie_missing_organisatie(self):
        catalogus = ProductenCatalogusFactory.create()
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=catalogus.lokale_overheid,
            organisatie=None,
        )
        ReferentieProductFactory.create(
            catalogus=catalogus,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        list_url = reverse("api:product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"][0]
        self.assertEqual(bevoegde_organisatie.naam, data["bevoegdeOrganisatie"]["naam"])
        self.assertIsNone(data["bevoegdeOrganisatie"]["owmsPrefLabel"])
        self.assertIsNone(data["bevoegdeOrganisatie"]["owmsIdentifier"])

    @freeze_time(NOW_DATE)
    def test_retrieve_product_by_uuid(self):
        product_version = ReferentieProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        product = product_version.product

        detail_url = reverse("api:product-detail", args=[product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(f"{product.uuid}", data["uuid"])
        self.assertEqual(f"{product.upn.upn_label}", data["upnLabel"])
        self.assertEqual(f"{product.upn.upn_uri}", data["upnUri"])
        self.assertEqual(product.product_valt_onder, data["productValtOnder"])
        self.assertEqual(
            product.bevoegde_organisatie.naam, data["bevoegdeOrganisatie"]["naam"]
        )
        self.assertEqual(1, data["versie"])
        self.assertEqual(
            f"http://testserver{reverse('api:productencatalogus-detail', args=[product.catalogus.uuid])}",
            data["catalogus"],
        )

        self.assertEqual(2, len(data["vertalingen"]))
        self.assertEqual(
            [
                {"label": "label1", "url": "https://example.com"},
                {"label": "label2", "url": "https://example2.com"},
            ],
            data["vertalingen"][0]["verwijzingLinks"],
        )
        self.assertEqual(0, len(data["locaties"]))
        self.assertEqual("", data["doelgroep"])
        self.assertEqual(0, len(data["gerelateerdeProducten"]))

    @freeze_time(NOW_DATE)
    def test_list_product_history(self):
        product_versie = ReferentieProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        product = product_versie.product
        ReferentieProductVersieFactory.create_batch(
            2, publicatie_datum=PAST_DATE, product=product
        )
        response = self.client.get(
            reverse("api:product-history-list", args=[product.uuid])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(3, len(data))

    @freeze_time(NOW_DATE)
    def test_list_product_history_does_not_return_concept(self):
        product_versie = ReferentieProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        product = product_versie.product
        ReferentieProductVersieFactory.create_batch(
            2, publicatie_datum=PAST_DATE, product=product
        )
        ReferentieProductVersieFactory.create(product=product, publicatie_datum=None)
        response = self.client.get(
            reverse("api:product-history-list", args=[product.uuid])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(3, len(data))

    @freeze_time(NOW_DATE)
    def test_list_product_concept(self):
        product = ReferentieProductFactory.create()
        ReferentieProductVersieFactory.create_batch(
            3, publicatie_datum=PAST_DATE, product=product
        )
        concept = ReferentieProductVersieFactory.create(
            publicatie_datum=None, product=product
        )

        response = self.client.get(
            reverse("api:product-concept-list", args=[product.uuid])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(1, len(data))
        self.assertEqual(concept.versie, data[0]["versie"])

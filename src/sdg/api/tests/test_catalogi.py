from datetime import timedelta

from django.utils.timezone import now

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory


class CatalogiTests(APITestCase):
    def test_list_catalogs(self):
        ProductenCatalogusFactory.create_batch(2)
        list_url = reverse("api:productencatalogus-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_list_catalogs_expired_organization(self):
        ProductenCatalogusFactory.create_batch(2)
        expired_org_catalog = ProductenCatalogusFactory.create(
            lokale_overheid__organisatie__owms_end_date=now() - timedelta(days=1),
        )
        list_url = reverse("api:productencatalogus-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))
        for catalog in data:
            self.assertNotEqual(catalog["uuid"], expired_org_catalog.uuid)

    def test_retrieve_catalog_by_uuid(self):
        catalog = ProductenCatalogusFactory.create()
        detail_url = reverse("api:productencatalogus-detail", args=[catalog.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(str(catalog.uuid), data["uuid"])

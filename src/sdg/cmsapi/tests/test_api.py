from datetime import date

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.accounts.tests.factories import UserFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import (
    BevoegdeOrganisatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedProductFactory,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductFactory,
    ProductVersieFactory,
    ReferentieProductFactory,
)


class ProductTranslationTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(
            email="test@email.com",
            password="h@1221$@fwDDW#3",
        )

        self.generic_product = GeneriekProductFactory.create()
        self.generic_localized_product_nl = LocalizedGeneriekProductFactory.create(
            generiek_product=self.generic_product, taal="nl"
        )
        self.generic_localized_product_en = LocalizedGeneriekProductFactory.create(
            generiek_product=self.generic_product, taal="en"
        )

        self.ref_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False
        )
        self.ref_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=self.ref_overheid,
            is_referentie_catalogus=True,
        )
        self.ref_product = ReferentieProductFactory.create(
            catalogus=self.ref_catalog,
            generiek_product=self.generic_product,
        )
        self.ref_product_versie = ProductVersieFactory.create(
            product=self.ref_product,
            publicatie_datum=date.today(),
        )
        self.ref_localized_product_nl = LocalizedProductFactory.create(
            product_versie=self.ref_product_versie,
            taal="nl",
        )
        self.ref_localized_product_en = LocalizedProductFactory.create(
            product_versie=self.ref_product_versie,
            taal="en",
        )

        self.overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=True
        )
        self.catalog = ProductenCatalogusFactory.create(
            lokale_overheid=self.overheid,
            is_referentie_catalogus=False,
        )
        self.bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=self.catalog.lokale_overheid,
            organisatie=None,
        )
        self.product = ProductFactory.create(
            catalogus=self.catalog,
            generiek_product=self.generic_product,
            referentie_product=self.ref_product,
            bevoegde_organisatie=self.bevoegde_organisatie,
        )
        self.product_versie = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=date.today(),
        )
        self.localized_product_nl = LocalizedProductFactory.create(
            product_versie=self.product_versie,
            taal="nl",
        )
        self.localized_product_en = LocalizedProductFactory.create(
            product_versie=self.product_versie,
            taal="en",
        )

    def test_api_call_with_no_params_while_logged_in(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse(
            "cmsapi:translation-list",
        )
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(0, len(data))

    def test_api_call_with_no_params_while_logged_out(self):
        list_url = reverse("cmsapi:translation-list")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_call_with_existing_product_id(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse("cmsapi:translation-list")

        response = self.client.get(f"{list_url}?product_id={self.product.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))
        self.assertEqual(
            str(data[0]["generiekProduct"]),
            str(self.generic_localized_product_nl.generiek_product),
        )
        self.assertEqual(
            str(data[1]["generiekProduct"]),
            str(self.generic_localized_product_en.generiek_product),
        )

    def test_api_call_with_none_existing_product_id(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse("cmsapi:translation-list")

        response = self.client.get(f"{list_url}?product_id={self.product.id + 1}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(0, len(data))

    def test_api_call_with_existing_product_id_and_none_existing_taal(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse("cmsapi:translation-list")

        response = self.client.get(f"{list_url}?product_id={self.product.id}&taal=uk")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(0, len(data))

    def test_api_call_with_existing_taal_and_none_existing_product_id(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse("cmsapi:translation-list")

        response = self.client.get(
            f"{list_url}?product_id={self.product.id + 1}&taal=nl"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(0, len(data))

    def test_api_call_with_existing_product_id_and_taal(self):
        self.client.force_authenticate(user=self.user)

        list_url = reverse("cmsapi:translation-list")

        response = self.client.get(f"{list_url}?product_id={self.product.id}&taal=nl")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(1, len(data))
        self.assertEqual(
            str(data[0]["generiekProduct"]),
            str(self.generic_localized_product_nl.generiek_product),
        )

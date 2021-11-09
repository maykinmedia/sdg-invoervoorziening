from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import (
    LokaleOverheidFactory,
    LokatieFactory,
)
from sdg.producten.tests.constants import NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
)


class CatalogiTests(APITestCase):
    def test_list_catalogs(self):
        ProductenCatalogusFactory.create_batch(2)
        list_url = reverse("productencatalogus-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_catalog_by_uuid(self):
        catalog = ProductenCatalogusFactory.create()
        detail_url = reverse("productencatalogus-detail", args=[catalog.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "uuid": str(catalog.uuid),
                "domein": catalog.domein,
                "naam": catalog.naam,
                "lokale_overheid": f"http://testserver{reverse('lokaleoverheid-detail', args=[catalog.lokale_overheid.uuid])}",
                "is_referentie_catalogus": catalog.is_referentie_catalogus,
                "referentie_catalogus": catalog.referentie_catalogus,
                "toelichting": catalog.toelichting,
                "versie": catalog.versie,
            },
            data,
        )


class ProductenTests(APITestCase):
    def test_list_products(self):
        ReferentieProductFactory.create_batch(2)
        list_url = reverse("product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    @freeze_time(NOW_DATE)
    def test_retrieve_product_by_uuid(self):
        product_version = ReferentieProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        product = product_version.product

        detail_url = reverse("product-detail", args=[product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["uuid"], str(product.uuid))
        self.assertEqual(data["upn_uri"], product.upn_uri)
        self.assertEqual(data["upn_label"], product.upn_label)
        self.assertEqual(data["beschikbaar"], product.beschikbaar)
        self.assertEqual(data["referentie_product"], product.referentie_product)
        self.assertEqual(data["is_referentie_product"], product.is_referentie_product)
        self.assertEqual(
            data["catalogus"],
            f"http://testserver{reverse('productencatalogus-detail', args=[product.catalogus.uuid])}",
        )

        self.assertEqual(0, len(data["gerelateerde_producten"]))
        self.assertEqual(2, len(data["vertalingen"]))
        self.assertEqual(0, len(data["doelgroep"]))
        self.assertEqual(0, len(data["lokaties"]))

    @freeze_time(NOW_DATE)
    def test_retrieve_history(self):
        product_versie = ReferentieProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        product = product_versie.product
        ReferentieProductVersieFactory.create_batch(
            2, publicatie_datum=PAST_DATE, product=product
        )
        response = self.client.get(reverse("product-history", args=[product.uuid]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(3, len(data))


class OrganisatiesTests(APITestCase):
    def test_list_organizations(self):
        LokaleOverheidFactory.create_batch(2)
        list_url = reverse("lokaleoverheid-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 2)

    def test_retrieve_organization_by_uuid(self):
        municipality = LokaleOverheidFactory.create()
        detail_url = reverse("lokaleoverheid-detail", args=[municipality.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "uuid": str(municipality.uuid),
                "organisatie": str(municipality.organisatie),
                "bevoegde_organisatie": str(municipality.bevoegde_organisatie),
                "ondersteunings_organisatie": str(
                    municipality.ondersteunings_organisatie
                ),
                "verantwoordelijke_organisatie": str(
                    municipality.verantwoordelijke_organisatie
                ),
                "lokaties": [],
            },
            data,
        )


class LocatiesTests(APITestCase):
    def test_list_locations(self):
        LokatieFactory.create_batch(2)
        list_url = reverse("lokatie-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_location_by_uuid(self):
        lokatie = LokatieFactory.create()
        detail_url = reverse("lokatie-detail", args=[lokatie.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "uuid": str(lokatie.uuid),
                "nummer": int(lokatie.nummer),
                "land": lokatie.land,
                "naam": lokatie.naam,
                "plaats": lokatie.plaats,
                "postcode": lokatie.postcode,
                "straat": lokatie.straat,
                "maandag": lokatie.maandag,
                "dinsdag": lokatie.dinsdag,
                "woensdag": lokatie.woensdag,
                "donderdag": lokatie.donderdag,
                "vrijdag": lokatie.vrijdag,
                "zaterdag": lokatie.zaterdag,
                "zondag": lokatie.zondag,
            },
            data,
        )

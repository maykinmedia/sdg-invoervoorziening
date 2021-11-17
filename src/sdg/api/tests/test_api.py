from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.serializers import ProductSerializer
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
        list_url = reverse("api:productencatalogus-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_catalog_by_uuid(self):
        catalog = ProductenCatalogusFactory.create()
        detail_url = reverse("api:productencatalogus-detail", args=[catalog.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "url": f"http://testserver{reverse('api:productencatalogus-detail', args=[catalog.uuid])}",
                "uuid": str(catalog.uuid),
                "domein": catalog.domein,
                "naam": catalog.naam,
                "producten": ProductSerializer(catalog.producten, many=True).data,
                "isReferentieCatalogus": catalog.is_referentie_catalogus,
                "referentieCatalogus": catalog.referentie_catalogus,
                "toelichting": catalog.toelichting,
                "versie": catalog.versie,
            },
            data,
        )


class ProductenTests(APITestCase):
    def test_list_products(self):
        ReferentieProductFactory.create_batch(2)
        list_url = reverse("api:product-list")

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

        detail_url = reverse("api:product-detail", args=[product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(f"{product.uuid}", data["uuid"])
        self.assertEqual(
            f"http://testserver{reverse('api:lokaleoverheid-detail', args=[product.catalogus.lokale_overheid.uuid])}",
            data["lokaleOverheid"],
        )
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

        self.assertEqual(0, len(data["lokaties"]))
        self.assertEqual(0, len(data["doelgroep"]))
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


class OrganisatiesTests(APITestCase):
    def test_list_organizations(self):
        LokaleOverheidFactory.create_batch(2)
        list_url = reverse("api:lokaleoverheid-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 2)

    def test_retrieve_organization_by_uuid(self):
        municipality = LokaleOverheidFactory.create()
        detail_url = reverse("api:lokaleoverheid-detail", args=[municipality.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "url": f"http://testserver{reverse('api:lokaleoverheid-detail', args=[municipality.uuid])}",
                "uuid": str(municipality.uuid),
                "organisatie": {
                    "owmsIdentifier": municipality.organisatie.owms_identifier,
                    "owmsPrefLabel": municipality.organisatie.owms_pref_label,
                    "owmsEndDate": municipality.organisatie.owms_end_date.isoformat(),
                },
                "lokaties": [],
                "catalogi": [],
                "contactNaam": municipality.contact_naam,
                "contactWebsite": municipality.contact_website,
                "contactEmailadres": municipality.contact_emailadres,
                "contactTelefoonnummer": municipality.contact_telefoonnummer,
                "bevoegdeOrganisatie": {
                    "owmsIdentifier": municipality.bevoegde_organisatie.owms_identifier,
                    "owmsPrefLabel": municipality.bevoegde_organisatie.owms_pref_label,
                    "owmsEndDate": municipality.bevoegde_organisatie.owms_end_date.isoformat(),
                },
                "ondersteuningsOrganisatie": {
                    "owmsIdentifier": municipality.ondersteunings_organisatie.owms_identifier,
                    "owmsPrefLabel": municipality.ondersteunings_organisatie.owms_pref_label,
                    "owmsEndDate": municipality.ondersteunings_organisatie.owms_end_date.isoformat(),
                },
                "verantwoordelijkeOrganisatie": {
                    "owmsIdentifier": municipality.verantwoordelijke_organisatie.owms_identifier,
                    "owmsPrefLabel": municipality.verantwoordelijke_organisatie.owms_pref_label,
                    "owmsEndDate": municipality.verantwoordelijke_organisatie.owms_end_date.isoformat(),
                },
            },
            data,
        )


class LocatiesTests(APITestCase):
    def test_list_locations(self):
        LokatieFactory.create_batch(2)
        list_url = reverse("api:lokatie-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_location_by_uuid(self):
        lokatie = LokatieFactory.create()
        detail_url = reverse("api:lokatie-detail", args=[lokatie.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "url": f"http://testserver{reverse('api:lokatie-detail', args=[lokatie.uuid])}",
                "uuid": str(lokatie.uuid),
                "nummer": int(lokatie.nummer),
                "land": lokatie.land,
                "naam": lokatie.naam,
                "plaats": lokatie.plaats,
                "postcode": lokatie.postcode,
                "straat": lokatie.straat,
                "openingstijden": {
                    "maandag": lokatie.maandag,
                    "dinsdag": lokatie.dinsdag,
                    "woensdag": lokatie.woensdag,
                    "donderdag": lokatie.donderdag,
                    "vrijdag": lokatie.vrijdag,
                    "zaterdag": lokatie.zaterdag,
                    "zondag": lokatie.zondag,
                },
            },
            data,
        )

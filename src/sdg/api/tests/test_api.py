import json

from django.test import TransactionTestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import (
    OverheidsorganisatieFactory,
    UniformeProductnaamFactory,
)
from sdg.organisaties.tests.factories.overheid import (
    BevoegdeOrganisatieFactory,
    LocatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductVersieFactory,
    ReferentieProductFactory,
    SpecifiekProductFactory,
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

        self.assertEqual(str(catalog.uuid), data["uuid"])


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
                "owmsIdentifier": municipality.organisatie.owms_identifier,
                "owmsPrefLabel": municipality.organisatie.owms_pref_label,
                "owmsEndDate": municipality.organisatie.owms_end_date.isoformat(),
                "locaties": [],
                "catalogi": [],
                "contactWebsite": municipality.contact_website,
                "contactEmailadres": municipality.contact_emailadres,
                "contactTelefoonnummer": municipality.contact_telefoonnummer,
                "bevoegdeOrganisaties": [],
                "ondersteuningsOrganisatie": {
                    "owmsIdentifier": municipality.ondersteunings_organisatie.owms_identifier,
                    "owmsPrefLabel": municipality.ondersteunings_organisatie.owms_pref_label,
                    "owmsEndDate": municipality.ondersteunings_organisatie.owms_end_date.isoformat(),
                },
            },
            data,
        )


class LocatiesTests(APITestCase):
    def test_list_locations(self):
        LocatieFactory.create_batch(2)
        list_url = reverse("api:locatie-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_location_by_uuid(self):
        locatie = LocatieFactory.create()
        detail_url = reverse("api:locatie-detail", args=[locatie.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(str(locatie.uuid), data["uuid"])

    def test_create_location_with_valid_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)
        detail_url = reverse("api:locatie-list")

        body = {
            "naam": "Lorem Ipsum",
            "straat": "Lorem Ipsum",
            "nummer": "12",
            "postcode": "1234AB",
            "plaats": "Lorem Ipsum",
            "land": "Lorem Ipsum",
            "openingstijden": {
                "maandag": ["12:00 - 18:00"],
                "dinsdag": ["12:00 - 18:00"],
                "woensdag": ["12:00 - 18:00"],
                "donderdag": ["12:00 - 18:00"],
                "vrijdag": ["12:00 - 18:00"],
                "zaterdag": ["12:00 - 18:00"],
                "zondag": ["12:00 - 18:00"],
            },
            "openingstijdenOpmerking": "Lorem Ipsum",
            "organisatie": {
                "owmsIdentifier": organisatie.owms_identifier,
                "owmsPrefLabel": organisatie.owms_pref_label,
                "owmsEndDate": organisatie.owms_end_date,
            },
        }

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_location_with_invalid_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)
        detail_url = reverse("api:locatie-list")

        body = {
            "naam": "Lorem Ipsum",
            "straat": "Lorem Ipsum",
            "nummer": "12",
            "postcode": "1234AB",
            "plaats": "Lorem Ipsum",
            "land": "Lorem Ipsum",
            "openingstijden": {
                "maandag": ["12:00 - 18:00"],
                "dinsdag": ["12:00 - 18:00"],
                "woensdag": ["12:00 - 18:00"],
                "donderdag": ["12:00 - 18:00"],
                "vrijdag": ["12:00 - 18:00"],
                "zaterdag": ["12:00 - 18:00"],
                "zondag": ["12:00 - 18:00"],
            },
            "openingstijdenOpmerking": "Lorem Ipsum",
            "organisatie": {
                "owmsIdentifier": "invalid owms identifier",
                "owmsPrefLabel": "invalid owms pref label",
                "owmsEndDate": None,
            },
        }

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_location_with_no_organisation_label_or_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)
        detail_url = reverse("api:locatie-list")

        body = {
            "naam": "Lorem Ipsum",
            "straat": "Lorem Ipsum",
            "nummer": "12",
            "postcode": "1234AB",
            "plaats": "Lorem Ipsum",
            "land": "Lorem Ipsum",
            "openingstijden": {
                "maandag": ["12:00 - 18:00"],
                "dinsdag": ["12:00 - 18:00"],
                "woensdag": ["12:00 - 18:00"],
                "donderdag": ["12:00 - 18:00"],
                "vrijdag": ["12:00 - 18:00"],
                "zaterdag": ["12:00 - 18:00"],
                "zondag": ["12:00 - 18:00"],
            },
            "openingstijdenOpmerking": "Lorem Ipsum",
            "organisatie": {
                "owmsEndDate": None,
            },
        }

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_location(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)
        detail_url = reverse("api:locatie-detail", args=[locatie.uuid])

        body = {
            "naam": "Lorem Ipsum",
            "straat": "Lorem Ipsum",
            "nummer": "12",
            "postcode": "1234AB",
            "plaats": "Lorem Ipsum",
            "land": "Lorem Ipsum",
            "openingstijden": {
                "maandag": ["12:00 - 18:00"],
                "dinsdag": ["12:00 - 18:00"],
                "woensdag": ["12:00 - 18:00"],
                "donderdag": ["12:00 - 18:00"],
                "vrijdag": ["12:00 - 18:00"],
                "zaterdag": ["12:00 - 18:00"],
                "zondag": ["12:00 - 18:00"],
            },
            "openingstijdenOpmerking": "Lorem Ipsum",
            "organisatie": {
                "owmsIdentifier": organisatie.owms_identifier,
                "owmsPrefLabel": organisatie.owms_pref_label,
                "owmsEndDate": organisatie.owms_end_date,
            },
        }

        response = self.client.put(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(str(locatie.uuid), data["uuid"])
        self.assertEqual(data["naam"], "Lorem Ipsum")
        self.assertEqual(data["straat"], "Lorem Ipsum")
        self.assertEqual(data["nummer"], "12")
        self.assertEqual(data["postcode"], "1234AB")
        self.assertEqual(data["plaats"], "Lorem Ipsum")
        self.assertEqual(data["naam"], "Lorem Ipsum")
        self.assertEqual(data["openingstijden"]["maandag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["dinsdag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["woensdag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["donderdag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["vrijdag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["zaterdag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijden"]["zondag"], ["12:00 - 18:00"])
        self.assertEqual(data["openingstijdenOpmerking"], "Lorem Ipsum")
        self.assertEqual(
            data["organisatie"]["owmsIdentifier"],
            "http://standaarden.overheid.nl/owms/terms/test",
        )
        self.assertEqual(data["organisatie"]["owmsPrefLabel"], "test")
        self.assertEqual(data["organisatie"]["owmsEndDate"], None)

    def test_delete_location(self):
        locatie = LocatieFactory.create()
        detail_url = reverse("api:locatie-detail", args=[locatie.uuid])

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        deleted_url = self.client.get(detail_url)

        self.assertEqual(deleted_url.status_code, status.HTTP_404_NOT_FOUND)


class ProductenTests(TransactionTestCase):
    def setUp(self):
        self.referentie_catalogus = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        self.upn = UniformeProductnaamFactory.create(
            upn_label="setup",
            upn_uri="https://www.setup.com",
        )
        self.generiek_product = GeneriekProductFactory.create(
            upn=self.upn,
        )
        self.referentie_product = ReferentieProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            product_aanwezig=True,
        )
        self.referentie_product_versie = ProductVersieFactory.create(
            product=self.referentie_product
        )
        self.referentie_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.referentie_product_versie
        )

        self.organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.setup.com",
            owms_pref_label="set up",
            owms_end_date=None,
        )
        self.lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.organisatie,
            contact_telefoonnummer="12317238712",
        )
        self.catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="set_up_catalogus",
        )
        self.product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus,
            product_aanwezig=True,
        )
        self.product_versie = ProductVersieFactory.create(product=self.product)
        self.localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.product_versie
        )

    def test_list_producten(self):
        list_url = reverse("api:product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_product_by_uuid(self):
        detail_url = reverse("api:product-detail", args=[self.product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(str(self.product.uuid), data["uuid"])

    def test_creating_product(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.test-creating-product.com",
            owms_pref_label="test_creating_product",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="1623612631",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="test_creating_product",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="test_creating_product",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": "2022-05-04",
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "test_creating_product",
                "owmsIdentifier": "https://www.test-creating-product.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_updating_product(self):
        detail_url = reverse("api:product-detail", args=[self.product.uuid])

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": "2022-05-04",
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": self.organisatie.owms_pref_label,
                "owmsIdentifier": self.organisatie.owms_identifier,
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        response = self.client.put(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(str(self.generiek_product.upn_label), data["upnLabel"])
        self.assertEqual(self.generiek_product.upn_uri, data["upnUri"])
        self.assertEqual(data["publicatieDatum"], "2022-05-04")
        self.assertEqual(data["productAanwezig"], 1)
        self.assertEqual(data["productValtOnder"], None)
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "set up"
        )
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )
        self.assertEqual(data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )
        self.assertEqual(data["locaties"], [])
        self.assertEqual(data["vertalingen"][0]["taal"], "nl")
        self.assertEqual(data["vertalingen"][0]["specifiekeTekst"], "")
        self.assertEqual(data["vertalingen"][0]["bewijs"], "")
        self.assertEqual(data["vertalingen"][0]["bezwaarEnBeroep"], "")
        self.assertEqual(data["vertalingen"][0]["decentraleProcedureLink"], "")
        self.assertEqual(data["vertalingen"][0]["kostenEnBetaalmethoden"], "")
        self.assertEqual(data["vertalingen"][0]["procedureBeschrijving"], "")
        self.assertEqual(data["vertalingen"][0]["productTitelDecentraal"], "")
        self.assertEqual(data["vertalingen"][0]["uitersteTermijn"], "")
        self.assertEqual(data["vertalingen"][0]["vereisten"], "")
        self.assertEqual(data["vertalingen"][0]["verwijzingLinks"], [])
        self.assertEqual(data["vertalingen"][0]["wtdBijGeenReactie"], "")
        self.assertEqual(data["vertalingen"][0]["productAanwezigToelichting"], "")
        self.assertEqual(data["vertalingen"][0]["productValtOnderToelichting"], "")

        self.assertEqual(data["vertalingen"][1]["taal"], "en")
        self.assertEqual(data["vertalingen"][1]["specifiekeTekst"], "")
        self.assertEqual(data["vertalingen"][1]["bewijs"], "")
        self.assertEqual(data["vertalingen"][1]["bezwaarEnBeroep"], "")
        self.assertEqual(data["vertalingen"][1]["decentraleProcedureLink"], "")
        self.assertEqual(data["vertalingen"][1]["kostenEnBetaalmethoden"], "")
        self.assertEqual(data["vertalingen"][1]["procedureBeschrijving"], "")
        self.assertEqual(data["vertalingen"][1]["productTitelDecentraal"], "")
        self.assertEqual(data["vertalingen"][1]["uitersteTermijn"], "")
        self.assertEqual(data["vertalingen"][1]["vereisten"], "")
        self.assertEqual(data["vertalingen"][1]["verwijzingLinks"], [])
        self.assertEqual(data["vertalingen"][1]["wtdBijGeenReactie"], "")
        self.assertEqual(data["vertalingen"][1]["productAanwezigToelichting"], "")
        self.assertEqual(data["vertalingen"][1]["productValtOnderToelichting"], "")
        self.assertEqual(data["gerelateerdeProducten"], [])

    def test_creating_product_with_upn_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.upn-label.com",
            owms_pref_label="upn_label",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="81623612838",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="upn_label",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="upn_label",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "upn_label",
                "owmsIdentifier": "https://www.upn-label.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["upnLabel"], "setup")
        self.assertEqual(create_data["upnUri"], "https://www.setup.com")

        with self.subTest("test_updating_product_with_upn_labe"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "publicatieDatum": "2022-05-04",
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "upn_label",
                    "owmsIdentifier": "https://www.upn-label.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["upnLabel"], "setup")
            self.assertEqual(update_data["upnUri"], "https://www.setup.com")

    def test_creating_product_with_upn_uri(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.upn-uri.com",
            owms_pref_label="upn_uri",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="63468216348613",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="upn_uri",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="upn_uri",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "upn_uri",
                "owmsIdentifier": "https://www.upn-uri.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["upnLabel"], "setup")
        self.assertEqual(create_data["upnUri"], "https://www.setup.com")

        with self.subTest("test_updating_product_with_upn_uri"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": "2022-05-04",
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "upn_uri",
                    "owmsIdentifier": "https://www.upn-uri.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["upnLabel"], "setup")
            self.assertEqual(update_data["upnUri"], "https://www.setup.com")

    def test_creating_product_with_verantwoordelijke_organisatie_identifier(
        self,
    ):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.verantwoordelijke-organisatie-identifier.com",
            owms_pref_label="verantwoordelijke_organisatie_identifier",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="234523452345",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="verantwoordelijke_organisatie_identifier",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="verantwoordelijke_organisatie_identifier",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsIdentifier": "https://www.verantwoordelijke-organisatie-identifier.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.verantwoordelijke-organisatie-identifier.com",
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
            "verantwoordelijke_organisatie_identifier",
        )

        with self.subTest(
            "test_updating_product_with_verantwoordelijke_organisatie_identifier"
        ):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsIdentifier": "https://www.verantwoordelijke-organisatie-identifier.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
                "https://www.verantwoordelijke-organisatie-identifier.com",
            )
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
                "verantwoordelijke_organisatie_identifier",
            )

    def test_creating_product_with_verantwoordelijke_organisatie_pref_label(
        self,
    ):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.verantwoordelijke-organisatie-pref-label.com",
            owms_pref_label="verantwoordelijke_organisatie_pref_label",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="73723472347234",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="verantwoordelijke_organisatie_pref_label",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="verantwoordelijke_organisatie_pref_label",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "verantwoordelijke_organisatie_pref_label",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.verantwoordelijke-organisatie-pref-label.com",
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
            "verantwoordelijke_organisatie_pref_label",
        )

        with self.subTest(
            "test_updating_product_with_verantwoordelijke_organisatie_pref_label"
        ):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "verantwoordelijke_organisatie_pref_label",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
                "https://www.verantwoordelijke-organisatie-pref-label.com",
            )
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
                "verantwoordelijke_organisatie_pref_label",
            )

    def test_creating_product_with_bevoegde_organisatie_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.bevoegde-organisatie-identifier.com",
            owms_pref_label="bevoegde_organisatie_identifier",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="82386482378",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="bevoegde_organisatie_identifier",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="bevoegde_organisatie_identifier",
        )

        second_organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.bevoegde-organisatie-identifier-2.com",
            owms_pref_label="bevoegde_organisatie_identifier_2",
            owms_end_date=None,
        )
        second_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=second_organisatie,
            contact_telefoonnummer="355124353",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=second_lokale_overheid,
            organisatie=second_organisatie,
            naam="bevoegde_organisatie_identifier_2",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=second_lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="bevoegde_organisatie_identifier_2",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsIdentifier": "http://www.bevoegde-organisatie-identifier.com",
                "owmsPrefLabel": "bevoegde_organisatie_identifier",
            },
            "bevoegdeOrganisatie": {
                "owmsIdentifier": "https://www.bevoegde-organisatie-identifier-2.com",
            },
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.bevoegde-organisatie-identifier-2.com",
        )
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
            "bevoegde_organisatie_identifier_2",
        )

        with self.subTest("test_updating_product_with_bevoegde_organisatie_identifier"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsIdentifier": "http://www.bevoegde-organisatie-identifier.com",
                    "owmsPrefLabel": "bevoegde_organisatie_identifier",
                },
                "bevoegdeOrganisatie": {
                    "owmsIdentifier": "https://www.bevoegde-organisatie-identifier-2.com",
                },
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsIdentifier"],
                "https://www.bevoegde-organisatie-identifier-2.com",
            )
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
                "bevoegde_organisatie_identifier_2",
            )

    def test_creating_product_with_bevoegde_organisatie_pref_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.bevoegde-organisatie-identifier.com",
            owms_pref_label="bevoegde_organisatie_identifier",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="82386482378",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="bevoegde_organisatie_identifier",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="bevoegde_organisatie_identifier",
        )

        second_organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.bevoegde-organisatie-identifier-2.com",
            owms_pref_label="bevoegde_organisatie_identifier_2",
            owms_end_date=None,
        )
        second_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=second_organisatie,
            contact_telefoonnummer="355124353",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=second_lokale_overheid,
            organisatie=second_organisatie,
            naam="bevoegde_organisatie_identifier_2",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsIdentifier": "http://www.bevoegde-organisatie-identifier.com",
                "owmsPrefLabel": "bevoegde_organisatie_identifier",
            },
            "bevoegdeOrganisatie": {
                "owmsPrefLabel": "bevoegde_organisatie_identifier_2",
            },
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.bevoegde-organisatie-identifier-2.com",
        )
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
            "bevoegde_organisatie_identifier_2",
        )

        with self.subTest("test_updating_product_with_bevoegde_organisatie_pref_label"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsIdentifier": "http://www.bevoegde-organisatie-identifier.com",
                    "owmsPrefLabel": "bevoegde_organisatie_identifier",
                },
                "bevoegdeOrganisatie": {
                    "owmsPrefLabel": "bevoegde_organisatie_identifier_2",
                },
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsIdentifier"],
                "https://www.bevoegde-organisatie-identifier-2.com",
            )
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
                "bevoegde_organisatie_identifier_2",
            )

    def test_creating_product_with_catalogus(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.with-catalogus.com",
            owms_pref_label="with_catalogus",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="51253568534",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="with_catalogus",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="with_catalogus",
        )

        catalogus_detail_url = reverse(
            "api:productencatalogus-detail", args=[catalogus.uuid]
        )
        catalogus_response = self.client.get(catalogus_detail_url)

        self.assertEqual(catalogus_response.status_code, status.HTTP_200_OK)

        catalogus_data = catalogus_response.json()

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "with_catalogus",
                "owmsIdentifier": "https://www.with-catalogus.com",
            },
            "bevoegdeOrganisatie": None,
            "catalogus": catalogus_data["url"],
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["catalogus"], catalogus_data["url"])

        with self.subTest("test_updating_product_with_catalogus"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "with_catalogus",
                    "owmsIdentifier": "https://www.with-catalogus.com",
                },
                "bevoegdeOrganisatie": None,
                "catalogus": catalogus_data["url"],
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["catalogus"], catalogus_data["url"])

    def test_creating_product_with_no_catalogus(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.without-catalogus.com",
            owms_pref_label="without_catalogus",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="79898123699",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="without_catalogus",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="without_catalogus",
        )

        catalogus_detail_url = reverse(
            "api:productencatalogus-detail", args=[catalogus.uuid]
        )
        catalogus_response = self.client.get(catalogus_detail_url)

        self.assertEqual(catalogus_response.status_code, status.HTTP_200_OK)

        catalogus_data = catalogus_response.json()

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "without_catalogus",
                "owmsIdentifier": "https://www.without-catalogus.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["catalogus"], catalogus_data["url"])

        with self.subTest("test_updating_product_with_no_catalogus"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "without_catalogus",
                    "owmsIdentifier": "https://www.without-catalogus.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["catalogus"], catalogus_data["url"])

    def test_creating_product_with_locaties_uuid(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.locaties-uuid.com",
            owms_pref_label="locaties_uuid",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="23412341234",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="locaties_uuid",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="locaties_uuid",
        )
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "locaties_uuid",
                "owmsIdentifier": "https://www.locaties-uuid.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [
                {
                    "uuid": str(locatie.uuid),
                }
            ],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie.naam)

        with self.subTest("test_updating_product_with_locaties_uuid"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "publicatieDatum": "2022-05-04",
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "locaties_uuid",
                    "owmsIdentifier": "https://www.locaties-uuid.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [
                    {
                        "uuid": str(locatie.uuid),
                    }
                ],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["locaties"][0]["uuid"], str(locatie.uuid))
            self.assertEqual(update_data["locaties"][0]["naam"], locatie.naam)

    def test_creating_product_with_locaties_naam(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.locaties-naam.com",
            owms_pref_label="locaties_naam",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="1231535613",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="locaties_naam",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="locaties_naam",
        )
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "locaties_naam",
                "owmsIdentifier": "https://www.locaties-naam.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [
                {
                    "naam": locatie.naam,
                }
            ],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie.naam)

        with self.subTest("test_updating_product_with_locaties_naam"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "publicatieDatum": "2022-05-04",
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "locaties_naam",
                    "owmsIdentifier": "https://www.locaties-naam.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [
                    {
                        "naam": locatie.naam,
                    }
                ],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "updated",
                        "bewijs": "updated",
                        "bezwaarEnBeroep": "updated",
                        "decentraleProcedureLink": "https://www.updated.com",
                        "kostenEnBetaalmethoden": "updated",
                        "procedureBeschrijving": "updated",
                        "productTitelDecentraal": "updated",
                        "uitersteTermijn": "updated",
                        "vereisten": "updated",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "updated",
                        "productAanwezigToelichting": "updated",
                        "productValtOnderToelichting": "updated",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()
            self.assertEqual(update_data["locaties"][0]["uuid"], str(locatie.uuid))
            self.assertEqual(update_data["locaties"][0]["naam"], locatie.naam)

    def test_creating_product_with_gerelateerde_producten_upn_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.gerelateerde-producten-upn-label.com",
            owms_pref_label="gerelateerde_producten_upn_label",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="21343587345",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="gerelateerde_producten_upn_label",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="gerelateerde_producten_upn_label",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "gerelateerde_producten_upn_label",
                "owmsIdentifier": "https://www.gerelateerde-producten-upn-label.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [
                {"upnLabel": self.product.generiek_product.upn.upn_label}
            ],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(create_data["gerelateerdeProducten"][0]["upnLabel"], "setup")
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            "https://www.setup.com",
        )

        with self.subTest(
            "test_updating_product_with_gerelateerde_producten_upn_label"
        ):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "gerelateerde_producten_upn_label",
                    "owmsIdentifier": "https://www.gerelateerde-producten-upn-label.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [
                    {"upnLabel": self.product.generiek_product.upn.upn_label}
                ],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnLabel"], "setup"
            )
            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnUri"],
                "https://www.setup.com",
            )

    def test_creating_product_with_gerelateerde_upn_uri(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.gerelateerde-producten-upn-uri.com",
            owms_pref_label="gerelateerde_producten_upn_uri",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="791273961",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="gerelateerde_producten_upn_uri",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="gerelateerde_producten_upn_uri",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "gerelateerde_producten_upn_uri",
                "owmsIdentifier": "https://www.gerelateerde-producten-upn-uri.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [
                {"upn_uri": self.product.generiek_product.upn.upn_uri}
            ],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(create_data["gerelateerdeProducten"][0]["upnLabel"], "setup")
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            "https://www.setup.com",
        )

        with self.subTest("test_updating_product_with_gerelateerde_upn_uri"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "gerelateerde_producten_upn_uri",
                    "owmsIdentifier": "https://www.gerelateerde-producten-upn-uri.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [
                    {"upn_uri": self.product.generiek_product.upn.upn_uri}
                ],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            create_data = create_response.json()

            self.assertEqual(
                create_data["gerelateerdeProducten"][0]["upnLabel"], "setup"
            )
            self.assertEqual(
                create_data["gerelateerdeProducten"][0]["upnUri"],
                "https://www.setup.com",
            )

    def test_creating_product_with_vertalingen_toelichtingen_when_allowed_with_label(
        self,
    ):
        referentie_catalogus = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            upn_label="second_product",
            upn_uri="https://www.second-product.com",
        )
        generiek_product = GeneriekProductFactory.create(
            upn=upn,
        )
        referentie_product = ReferentieProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=None,
            catalogus=referentie_catalogus,
            product_aanwezig=True,
        )
        referentie_product_versie = ProductVersieFactory.create(
            product=referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=referentie_product_versie
        )

        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.toelichtingen-when-allowed-with-label.com",
            owms_pref_label="toelichtingen_when_allowed_with_label",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="4712369373",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="toelichtingen_when_allowed_with_label",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(product=second_product)
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 0,
            "productValtOnder": {
                "upnLabel": second_product.generiek_product.upn.upn_label,
            },
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "toelichtingen_when_allowed_with_label",
                "owmsIdentifier": "https://www.toelichtingen-when-allowed-with-label.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "Tekst",
                    "productValtOnderToelichting": "Tekst",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "Text",
                    "productValtOnderToelichting": "Text",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertFalse(create_data["productAanwezig"])
        self.assertEqual(create_data["productValtOnder"]["upnLabel"], "second_product")
        self.assertEqual(
            create_data["productValtOnder"]["upnUri"], "https://www.second-product.com"
        )
        self.assertEqual(
            create_data["vertalingen"][0]["productAanwezigToelichting"], "Tekst"
        )
        self.assertEqual(
            create_data["vertalingen"][0]["productValtOnderToelichting"], "Tekst"
        )

        self.assertEqual(
            create_data["vertalingen"][1]["productAanwezigToelichting"], "Text"
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productValtOnderToelichting"], "Text"
        )

        with self.subTest(
            "test_updating_product_with_vertalingen_toelichtingen_when_allowed_with_label"
        ):
            detail_url = reverse("api:product-detail", args=[self.product.uuid])

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 0,
                "productValtOnder": {
                    "upnLabel": second_product.generiek_product.upn.upn_label,
                },
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "toelichtingen_when_allowed_with_label",
                    "owmsIdentifier": "https://www.toelichtingen-when-allowed-with-label.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "Updated Tekst",
                        "productValtOnderToelichting": "Updated Tekst",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "Updated Text",
                        "productValtOnderToelichting": "Updated Text",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            update_data = response.json()

            self.assertFalse(update_data["productAanwezig"])
            self.assertEqual(
                update_data["productValtOnder"]["upnLabel"], "second_product"
            )
            self.assertEqual(
                update_data["productValtOnder"]["upnUri"],
                "https://www.second-product.com",
            )
            self.assertEqual(
                update_data["vertalingen"][0]["productAanwezigToelichting"],
                "Updated Tekst",
            )
            self.assertEqual(
                update_data["vertalingen"][0]["productValtOnderToelichting"],
                "Updated Tekst",
            )

            self.assertEqual(
                update_data["vertalingen"][1]["productAanwezigToelichting"],
                "Updated Text",
            )
            self.assertEqual(
                update_data["vertalingen"][1]["productValtOnderToelichting"],
                "Updated Text",
            )

    def test_creating_product_with_vertalingen_toelichtingen_when_allowed_with_uri(
        self,
    ):
        referentie_catalogus = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            upn_label="second_product",
            upn_uri="https://www.second-product.com",
        )
        generiek_product = GeneriekProductFactory.create(
            upn=upn,
        )
        referentie_product = ReferentieProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=None,
            catalogus=referentie_catalogus,
            product_aanwezig=True,
        )
        referentie_product_versie = ProductVersieFactory.create(
            product=referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=referentie_product_versie
        )

        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.toelichtingen-when-allowed-with-uri.com",
            owms_pref_label="toelichtingen_when_allowed_with_uri",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="342523452323",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="toelichtingen_when_allowed_with_uri",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(product=second_product)
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 0,
            "productValtOnder": {
                "upnUri": second_product.generiek_product.upn.upn_uri,
            },
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "toelichtingen_when_allowed_with_uri",
                "owmsIdentifier": "https://www.toelichtingen-when-allowed-with-uri.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "Tekst",
                    "productValtOnderToelichting": "Tekst",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "Text",
                    "productValtOnderToelichting": "Text",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertFalse(create_data["productAanwezig"])
        self.assertEqual(create_data["productValtOnder"]["upnLabel"], "second_product")
        self.assertEqual(
            create_data["productValtOnder"]["upnUri"],
            "https://www.second-product.com",
        )
        self.assertEqual(
            create_data["vertalingen"][0]["productAanwezigToelichting"],
            "Tekst",
        )
        self.assertEqual(
            create_data["vertalingen"][0]["productValtOnderToelichting"],
            "Tekst",
        )

        self.assertEqual(
            create_data["vertalingen"][1]["productAanwezigToelichting"],
            "Text",
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productValtOnderToelichting"],
            "Text",
        )

        with self.subTest(
            "test_updating_product_with_vertalingen_toelichtingen_when_allowed_with_uri"
        ):
            detail_url = reverse("api:product-detail", args=[self.product.uuid])

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 0,
                "productValtOnder": {
                    "upnUri": second_product.generiek_product.upn.upn_uri,
                },
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "toelichtingen_when_allowed_with_uri",
                    "owmsIdentifier": "https://www.toelichtingen-when-allowed-with-uri.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "Updated Tekst",
                        "productValtOnderToelichting": "Updated Tekst",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "Updated Text",
                        "productValtOnderToelichting": "Updated Text",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(
                data["vertalingen"][0]["productAanwezigToelichting"], "Updated Tekst"
            )
            self.assertEqual(
                data["vertalingen"][0]["productValtOnderToelichting"], "Updated Tekst"
            )

            self.assertEqual(
                data["vertalingen"][1]["productAanwezigToelichting"], "Updated Text"
            )
            self.assertEqual(
                data["vertalingen"][1]["productValtOnderToelichting"], "Updated Text"
            )

    def test_creating_product_without_vertalingen_toelichtingen_when_product_valt_onder(
        self,
    ):
        referentie_catalogus = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            upn_label="second_product",
            upn_uri="https://www.second-product.com",
        )
        generiek_product = GeneriekProductFactory.create(
            upn=upn,
        )
        referentie_product = ReferentieProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=None,
            catalogus=referentie_catalogus,
            product_aanwezig=True,
        )
        referentie_product_versie = ProductVersieFactory.create(
            product=referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=referentie_product_versie
        )

        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.without-vertalingen-toelichtingen-when-product-valt-onder.com",
            owms_pref_label="without_vertalingen_toelichtingen_when_product_valt_onder",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123856734524",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="without_vertalingen_toelichtingen_when_product_valt_onder",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(product=second_product)
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": {
                "upnLabel": second_product.generiek_product.upn.upn_label,
                "upnUri": second_product.generiek_product.upn.upn_uri,
            },
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "without_vertalingen_toelichtingen_when_product_valt_onder",
                "owmsIdentifier": "https://www.without-vertalingen-toelichtingen-when-product-valt-onder.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest(
            "test_updating_product_without_vertalingen_toelichtingen_when_product_valt_onder"
        ):
            detail_url = reverse("api:product-detail", args=[self.product.uuid])

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": {
                    "upnLabel": second_product.generiek_product.upn.upn_label,
                    "upnUri": second_product.generiek_product.upn.upn_uri,
                },
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "without_vertalingen_toelichtingen_when_product_valt_onder",
                    "owmsIdentifier": "https://www.without-vertalingen-toelichtingen-when-product-valt-onder.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_product_without_vertalingen_toelichtingen_when_no_product_aanwezig(
        self,
    ):
        referentie_catalogus = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            upn_label="second_product",
            upn_uri="https://www.second-product.com",
        )
        generiek_product = GeneriekProductFactory.create(
            upn=upn,
        )
        referentie_product = ReferentieProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=None,
            catalogus=referentie_catalogus,
            product_aanwezig=True,
        )
        referentie_product_versie = ProductVersieFactory.create(
            product=referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=referentie_product_versie
        )

        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.without-vertalingen-toelichtingen-when-no-product-aanwezig.com",
            owms_pref_label="without_vertalingen_toelichtingen_when_no_product_aanwezig",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123346468235",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="without_vertalingen_toelichtingen_when_no_product_aanwezig",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            referentie_product=referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(product=second_product)
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 0,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "without_vertalingen_toelichtingen_when_no_product_aanwezig",
                "owmsIdentifier": "https://www.without-vertalingen-toelichtingen-when-no-product-aanwezig.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [],
            "vertalingen": [
                {
                    "taal": "nl",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
                {
                    "taal": "en",
                    "specifiekeTekst": "",
                    "bewijs": "",
                    "bezwaarEnBeroep": "",
                    "decentraleProcedureLink": "",
                    "kostenEnBetaalmethoden": "",
                    "procedureBeschrijving": "",
                    "productTitelDecentraal": "",
                    "uitersteTermijn": "",
                    "vereisten": "",
                    "verwijzingLinks": [],
                    "wtdBijGeenReactie": "",
                    "productAanwezigToelichting": "",
                    "productValtOnderToelichting": "",
                },
            ],
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest(
            "test_updating_product_without_vertalingen_toelichtingen_when_no_product_aanwezig"
        ):
            detail_url = reverse("api:product-detail", args=[self.product.uuid])

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 0,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "without_vertalingen_toelichtingen_when_no_product_aanwezig",
                    "owmsIdentifier": "https://www.without-vertalingen-toelichtingen-when-no-product-aanwezig.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [],
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "",
                        "bewijs": "",
                        "bezwaarEnBeroep": "",
                        "decentraleProcedureLink": "",
                        "kostenEnBetaalmethoden": "",
                        "procedureBeschrijving": "",
                        "productTitelDecentraal": "",
                        "uitersteTermijn": "",
                        "vereisten": "",
                        "verwijzingLinks": [],
                        "wtdBijGeenReactie": "",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
                "gerelateerdeProducten": [],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
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
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

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
                "owmsPrefLabel": organisatie.owms_pref_label,
                "owmsEndDate": organisatie.owms_end_date,
            },
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_location_with_valid_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

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
                "owmsEndDate": organisatie.owms_end_date,
            },
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
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
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

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

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_location_with_no_organisation_label_or_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

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

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.post(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
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
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

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

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.put(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
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
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid
        )

        detail_url = reverse("api:locatie-detail", args=[locatie.uuid])

        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        response = self.client.delete(
            detail_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        deleted_url = self.client.get(detail_url)

        self.assertEqual(deleted_url.status_code, status.HTTP_404_NOT_FOUND)

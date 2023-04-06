import json
from datetime import timedelta

from django.test import override_settings
from django.utils.timezone import now

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
)


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
class OrganisatiesTests(APITestCase):
    def test_list_organizations(self):
        LokaleOverheidFactory.create_batch(2)
        list_url = reverse("api:lokaleoverheid-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 2)

    def test_list_organizations_expired_organization(self):
        LokaleOverheidFactory.create_batch(2)
        expired_org = LokaleOverheidFactory.create(
            organisatie__owms_end_date=now() - timedelta(days=1)
        )
        list_url = reverse("api:lokaleoverheid-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 2)
        for org in data:
            self.assertNotEqual(org["uuid"], expired_org.uuid)

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
                "owmsEndDate": None,
                "locaties": [],
                "catalogi": [],
                "contactWebsite": municipality.contact_website,
                "contactEmailadres": municipality.contact_emailadres,
                "contactTelefoonnummer": municipality.contact_telefoonnummer,
                "contactFormulierLink": municipality.contact_formulier_link,
                "bevoegdeOrganisaties": [],
            },
            data,
        )

    def test_update_organization_with_valid_values(self):
        municipality = LokaleOverheidFactory.create()
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=municipality
        )

        detail_url = reverse("api:lokaleoverheid-detail", args=[municipality.uuid])
        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}
        body = {
            "contactWebsite": "https://test.com",
            "contactEmailadres": "test@test.test",
            "contactTelefoonnummer": "06123456789",
            "contactFormulierLink": "https://www.test.com",
        }

        response = self.client.put(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            {
                "contactWebsite": "https://test.com",
                "contactEmailadres": "test@test.test",
                "contactTelefoonnummer": "06123456789",
                "contactFormulierLink": "https://www.test.com",
            },
            data,
        )

    def test_update_organization_with_invalid_values(self):
        municipality = LokaleOverheidFactory.create()
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=municipality
        )

        detail_url = reverse("api:lokaleoverheid-detail", args=[municipality.uuid])
        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}

        body = {
            "contactWebsite": "test",
            "contactEmailadres": "test",
            "contactTelefoonnummer": [],
            "contactFormulierLink": "test",
        }

        response = self.client.put(
            detail_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(
            [
                {
                    "name": "contactWebsite",
                    "code": "invalid",
                    "reason": "De URL moet beginnen met 'https://'. Let op de 's' achter 'http'.",
                },
                {
                    "name": "contactWebsite",
                    "code": "invalid",
                    "reason": "Voer een geldige URL in.",
                },
                {
                    "name": "contactEmailadres",
                    "code": "invalid",
                    "reason": "Voer een geldig e-mailadres in.",
                },
                {
                    "name": "contactTelefoonnummer",
                    "code": "invalid",
                    "reason": "Not a valid string.",
                },
                {
                    "name": "contactFormulierLink",
                    "code": "invalid",
                    "reason": "De URL moet beginnen met 'https://'. Let op de 's' achter 'http'.",
                },
                {
                    "name": "contactFormulierLink",
                    "code": "invalid",
                    "reason": "Voer een geldige URL in.",
                },
            ],
            data["invalidParams"],
        )


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
class LocatiesTests(APITestCase):
    def test_list_locations(self):
        LocatieFactory.create_batch(2)
        list_url = reverse("api:locatie-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(2, len(data))

    def test_retrieve_location_by_naam(self):
        locatie = LocatieFactory.create()
        detail_url = reverse("api:locatie-detail", args=[locatie.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(str(locatie.naam), data["naam"])

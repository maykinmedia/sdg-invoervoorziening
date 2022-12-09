from django.test import override_settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
    OverheidsorganisatieFactory,
)


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
class APIAuthTest(APITestCase):
    def setUp(self):
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
        self.token = token_authorization.token

        self.list_url = reverse("api:locatie-list")

    def test_api_call_without_token(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_call_with_invalid_token(self):
        headers = {"HTTP_AUTHORIZATION": "Token foobar"}

        response = self.client.get(self.list_url, **headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_call_with_valid_token(self):
        headers = {"HTTP_AUTHORIZATION": f"Token {self.token}"}

        response = self.client.get(self.list_url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

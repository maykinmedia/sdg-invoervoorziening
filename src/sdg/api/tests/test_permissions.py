from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
    OverheidsorganisatieFactory,
)


class LocationPermissieTest(APITestCase):
    def test_api_call_of_safe_method_without_token(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        LocatieFactory.create(lokale_overheid=lokale_overheid)

        list_url = reverse("api:locatie-list")
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_call_of_delete_method_without_a_token(self):
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

        list_url = reverse("api:locatie-list")
        response = self.client.get(
            list_url, header={"Authorization": f"Token {token_authorization.token}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_call_of_delete_method_with_the_wrong_token(self):
        pass

    def test_api_call_of_delete_method_with_the_correct_token(self):
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

        list_url = reverse("api:locatie-delete")
        response = self.client.get(
            list_url, header={"Authorization": f"Token {token_authorization.token}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

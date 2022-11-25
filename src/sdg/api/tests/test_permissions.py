from django.test import RequestFactory, override_settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.api.views.organisaties import LocatieViewSet
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
    OverheidsorganisatieFactory,
)


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
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
        TokenAuthorizationFactory.create(lokale_overheid=lokale_overheid)

        list_url = reverse("api:locatie-list")
        response = response = self.client.delete(
            list_url,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_call_of_delete_method_with_the_wrong_token(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)

        seccond_lokale_overheid = LokaleOverheidFactory.create()
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=seccond_lokale_overheid
        )

        list_url = reverse("api:locatie-detail", args=[locatie.uuid])
        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}
        response = self.client.delete(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_call_of_delete_method_with_the_correct_token(self):
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

        list_url = reverse("api:locatie-detail", args=[locatie.uuid])
        headers = {"HTTP_AUTHORIZATION": f"Token {token_authorization.token}"}
        response = self.client.delete(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @override_settings(SDG_API_WHITELISTING_ENABLED=True)
    def test_api_white_list_with_correct_ip(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid,
            token__whitelisted_ips=["127.0.0.1"],
        )

        list_url = reverse("api:locatie-detail", args=[locatie.uuid])
        headers = {
            "HTTP_AUTHORIZATION": f"Token {token_authorization.token}",
            "HTTP_X_REAL_IP": "127.0.0.1",
        }

        request = RequestFactory().delete(
            list_url,
            content_type="application/json",
            **headers,
        )

        response = LocatieViewSet.as_view(
            {"delete": "destroy"},
        )(request, uuid=locatie.uuid)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @override_settings(SDG_API_WHITELISTING_ENABLED=True)
    def test_api_white_list_with_incorrect_ip(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="http://standaarden.overheid.nl/owms/terms/test",
            owms_pref_label="test",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(organisatie=organisatie)
        locatie = LocatieFactory.create(lokale_overheid=lokale_overheid)
        token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=lokale_overheid,
            token__whitelisted_ips=["127.0.0.1"],
        )

        list_url = reverse("api:locatie-detail", args=[locatie.uuid])
        headers = {
            "HTTP_AUTHORIZATION": f"Token {token_authorization.token}",
            "HTTP_X_REAL_IP": "59.227.39.14",
        }

        request = RequestFactory().delete(
            list_url,
            content_type="application/json",
            **headers,
        )

        response = LocatieViewSet.as_view(
            {"delete": "destroy"},
        )(request, uuid=locatie.uuid)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

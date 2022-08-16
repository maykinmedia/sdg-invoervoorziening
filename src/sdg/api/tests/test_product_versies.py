import json
from datetime import timedelta

from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from sdg.api.tests.factories.token import TokenAuthorizationFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import (
    OverheidsorganisatieFactory,
    UniformeProductnaamFactory,
)
from sdg.organisaties.tests.factories.overheid import (
    BevoegdeOrganisatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.constants import FUTURE_DATE, NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedProductFactory,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductVersieFactory,
    SpecifiekProductFactory,
)


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
class ProductenVersieTest(APITestCase):
    def get_product_post_body(self, overrides):
        new_body = self.body
        new_body.update(overrides)
        return new_body

    def setUp(self):
        self.upn = UniformeProductnaamFactory.create(
            upn_label="setup",
            upn_uri="https://www.setup.com",
        )
        self.generiek_product = GeneriekProductFactory.create(
            upn=self.upn,
            doelgroep="eu-burger",
        )
        LocalizedGeneriekProductFactory.create_batch(
            2, generiek_product=self.generiek_product
        )

        self.referentie_organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.referentie.com",
            owms_pref_label="referentie",
            owms_end_date=None,
        )
        self.referentie_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.referentie_organisatie,
            contact_telefoonnummer="98573415236748",
        )
        self.referentie_token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=self.referentie_lokale_overheid
        )
        self.referentie_bevoegde_organisatie = BevoegdeOrganisatieFactory(
            organisatie=self.referentie_organisatie,
            lokale_overheid=self.referentie_lokale_overheid,
        )
        self.referentie_catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=self.referentie_lokale_overheid,
            is_referentie_catalogus=True,
            is_default_catalogus=True,
            naam="referentie_catalogus",
        )
        self.referentie_product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            product_aanwezig=True,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
        )
        self.referentie_product_versie = ProductVersieFactory.create(
            product=self.referentie_product,
            versie=1,
            publicatie_datum=PAST_DATE,
        )
        self.referentie_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.referentie_product_versie
        )

        self.organisatie_publicatie_datum_none = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.none.com",
            owms_pref_label="none",
            owms_end_date=None,
        )
        self.lokale_overheid_publicatie_datum_none = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.organisatie_publicatie_datum_none,
            contact_telefoonnummer="12317238712",
        )
        self.token_authorization_publicatie_datum_none = (
            TokenAuthorizationFactory.create(
                lokale_overheid=self.lokale_overheid_publicatie_datum_none
            )
        )
        self.bevoegde_organisatie_publicatie_datum_none = (
            BevoegdeOrganisatieFactory.create(
                organisatie=self.organisatie_publicatie_datum_none,
                lokale_overheid=self.lokale_overheid_publicatie_datum_none,
            )
        )
        self.catalogus_publicatie_datum_none = ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid_publicatie_datum_none,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="none_catalogus",
        )
        self.product_publicatie_datum_none = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus_publicatie_datum_none,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie_publicatie_datum_none,
        )
        self.product_versie_publicatie_datum_none = ProductVersieFactory.create(
            product=self.product_publicatie_datum_none,
            versie=2,
            publicatie_datum=None,
        )
        self.localized_products_publicatie_datum_none = (
            LocalizedProductFactory.create_batch(
                2, product_versie=self.product_versie_publicatie_datum_none
            )
        )

        self.organisatie_publicatie_datum_today = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.today.com",
            owms_pref_label="today",
            owms_end_date=None,
        )
        self.lokale_overheid_publicatie_datum_today = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.organisatie_publicatie_datum_today,
            contact_telefoonnummer="9082743977",
        )
        self.token_authorization_publicatie_datum_today = (
            TokenAuthorizationFactory.create(
                lokale_overheid=self.lokale_overheid_publicatie_datum_today
            )
        )
        self.bevoegde_organisatie_publicatie_datum_today = (
            BevoegdeOrganisatieFactory.create(
                organisatie=self.organisatie_publicatie_datum_today,
                lokale_overheid=self.lokale_overheid_publicatie_datum_today,
            )
        )
        self.catalogus_publicatie_datum_today = ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid_publicatie_datum_today,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="today_catalogus",
        )
        self.product_publicatie_datum_today = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus_publicatie_datum_today,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie_publicatie_datum_today,
        )
        self.product_versie_publicatie_datum_today = ProductVersieFactory.create(
            product=self.product_publicatie_datum_today,
            versie=2,
            publicatie_datum=NOW_DATE,
        )
        self.localized_products_publicatie_datum_today = (
            LocalizedProductFactory.create_batch(
                2, product_versie=self.product_versie_publicatie_datum_today
            )
        )

        self.organisatie_publicatie_datum_future = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.future.com",
            owms_pref_label="future",
            owms_end_date=None,
        )
        self.lokale_overheid_publicatie_datum_future = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.organisatie_publicatie_datum_future,
            contact_telefoonnummer=" 296492349892",
        )
        self.token_authorization_publicatie_datum_future = (
            TokenAuthorizationFactory.create(
                lokale_overheid=self.lokale_overheid_publicatie_datum_future
            )
        )
        self.bevoegde_organisatie_publicatie_datum_future = (
            BevoegdeOrganisatieFactory.create(
                organisatie=self.organisatie_publicatie_datum_future,
                lokale_overheid=self.lokale_overheid_publicatie_datum_future,
            )
        )
        self.catalogus_publicatie_datum_future = ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid_publicatie_datum_future,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="future_catalogus",
        )
        self.product_publicatie_datum_future = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus_publicatie_datum_future,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie_publicatie_datum_future,
        )
        self.product_versie_publicatie_datum_future = ProductVersieFactory.create(
            product=self.product_publicatie_datum_future,
            versie=2,
            publicatie_datum=FUTURE_DATE,
        )
        self.localized_products_publicatie_datum_future = (
            LocalizedProductFactory.create_batch(
                2, product_versie=self.product_versie_publicatie_datum_future
            )
        )

        self.organisatie_publicatie_datum_past = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.past.com",
            owms_pref_label="past",
            owms_end_date=None,
        )
        self.lokale_overheid_publicatie_datum_past = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.organisatie_publicatie_datum_past,
            contact_telefoonnummer="12317238712",
        )
        self.token_authorization_publicatie_datum_past = (
            TokenAuthorizationFactory.create(
                lokale_overheid=self.lokale_overheid_publicatie_datum_past
            )
        )
        self.bevoegde_organisatie_publicatie_datum_past = (
            BevoegdeOrganisatieFactory.create(
                organisatie=self.organisatie_publicatie_datum_past,
                lokale_overheid=self.lokale_overheid_publicatie_datum_past,
            )
        )
        self.catalogus_publicatie_datum_past = ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid_publicatie_datum_past,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="past_catalogus",
        )
        self.product_publicatie_datum_past = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus_publicatie_datum_past,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie_publicatie_datum_past,
        )
        self.product_versie_publicatie_datum_past = ProductVersieFactory.create(
            product=self.product_publicatie_datum_past,
            versie=2,
            publicatie_datum=PAST_DATE,
        )
        self.localized_products_publicatie_datum_past = (
            LocalizedProductFactory.create_batch(
                2, product_versie=self.product_versie_publicatie_datum_past
            )
        )

        self.body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "doelgroep": "eu-burger",
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": None,
                "owmsIdentifier": None,
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

    @freeze_time(NOW_DATE)
    def test_product_version_none_to_today(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "none",
                    "owmsIdentifier": "https://www.none.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_none.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_none_to_future(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(FUTURE_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "none",
                    "owmsIdentifier": "https://www.none.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_none.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_none_to_none(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "none",
                    "owmsIdentifier": "https://www.none.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_none.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_none_to_past(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(PAST_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "none",
                    "owmsIdentifier": "https://www.none.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_none.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_today_to_today(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "today",
                    "owmsIdentifier": "https://www.today.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_today.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_today_to_future(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(FUTURE_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "today",
                    "owmsIdentifier": "https://www.today.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_today.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_today_to_none(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "today",
                    "owmsIdentifier": "https://www.today.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_today.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_today_to_past(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(PAST_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "today",
                    "owmsIdentifier": "https://www.today.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_today.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time(NOW_DATE)
    def test_product_version_future_to_today(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "future",
                    "owmsIdentifier": "https://www.future.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_future.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_future_to_future(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(FUTURE_DATE + timedelta(days=1)),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "future",
                    "owmsIdentifier": "https://www.future.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_future.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_future_to_none(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "future",
                    "owmsIdentifier": "https://www.future.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_future.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 2)

    @freeze_time(NOW_DATE)
    def test_product_version_future_to_past(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(PAST_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "future",
                    "owmsIdentifier": "https://www.future.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_future.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time(NOW_DATE)
    def test_product_version_past_to_today(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "past",
                    "owmsIdentifier": "https://www.past.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_past.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_past_to_future(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(FUTURE_DATE),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "past",
                    "owmsIdentifier": "https://www.past.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_past.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_past_to_none(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "past",
                    "owmsIdentifier": "https://www.past.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_past.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["versie"], 3)

    @freeze_time(NOW_DATE)
    def test_product_version_past_to_past(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(PAST_DATE - timedelta(days=1)),
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "past",
                    "owmsIdentifier": "https://www.past.com",
                },
            }
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token_authorization_publicatie_datum_past.token}"
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

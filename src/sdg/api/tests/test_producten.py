import json

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
    LocatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.constants import FUTURE_DATE, NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductVersieFactory,
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductFactory,
)


@override_settings(WHITELISTING_ENABLED=False)
class ProductenTests(APITestCase):
    def get_product_post_body(self, overrides):
        new_body = self.body
        new_body.update(overrides)
        return new_body

    def setUp(self):
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
        self.upn = UniformeProductnaamFactory.create(
            upn_label="setup",
            upn_uri="https://www.setup.com",
        )
        self.generiek_product = GeneriekProductFactory.create(
            upn=self.upn,
            doelgroep="eu-burger",
        )
        self.referentie_product = ReferentieProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
            product_aanwezig=True,
        )
        self.referentie_product_versie = ProductVersieFactory.create(
            product=self.referentie_product
        )
        self.referentie_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.referentie_product_versie
        )

        self.second_upn = UniformeProductnaamFactory.create(
            upn_label="second_setup",
            upn_uri="https://www.second-setup.com",
        )
        self.second_generiek_product = GeneriekProductFactory.create(
            upn=self.second_upn,
            doelgroep="eu-burger",
        )
        self.second_referentie_product = ReferentieProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
            product_aanwezig=True,
        )
        self.second_referentie_product_versie = ProductVersieFactory.create(
            product=self.second_referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=self.second_referentie_product_versie
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
        self.token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=self.lokale_overheid
        )
        self.bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            organisatie=self.organisatie, lokale_overheid=self.lokale_overheid
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
            bevoegde_organisatie=self.bevoegde_organisatie,
        )
        self.product_versie = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
        )
        self.localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.product_versie
        )

        self.seccond_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=self.catalogus,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie,
        )
        self.second_product_versie = ProductVersieFactory.create(
            product=self.seccond_product,
            publicatie_datum=None,
        )
        self.second_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.second_product_versie
        )

        self.test_organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        self.test_lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=self.test_organisatie,
            contact_telefoonnummer="123456789",
        )
        self.test_token_authorization = TokenAuthorizationFactory.create(
            lokale_overheid=self.test_lokale_overheid
        )
        self.test_bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=self.test_lokale_overheid,
            organisatie=self.test_organisatie,
            naam="organisatie",
        )
        self.test_catalog = ProductenCatalogusFactory.create(
            lokale_overheid=self.test_lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        self.test_product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            bevoegde_organisatie=self.test_bevoegde_organisatie,
            catalogus=self.test_catalog,
            product_aanwezig=True,
        )
        self.test_product_versie = ProductVersieFactory.create(
            product=self.test_product,
            publicatie_datum=None,
            versie=1,
        )
        LocalizedProductFactory.create_batch(
            2,
            product_versie=self.test_product_versie,
        )

        self.second_test_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            bevoegde_organisatie=self.test_bevoegde_organisatie,
            catalogus=self.test_catalog,
            product_aanwezig=True,
        )
        self.second_test_product_versie = ProductVersieFactory.create(
            product=self.second_test_product, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=self.second_test_product_versie
        )

        self.body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "doelgroep": "eu-burger",
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "organisatie",
                "owmsIdentifier": "https://www.organisatie.com",
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

    def test_list_producten(self):
        list_url = reverse("api:product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(6, len(data))

    def test_retrieve_product_by_uuid(self):
        detail_url = reverse("api:product-detail", args=[self.product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(str(self.product.uuid), data["uuid"])

    def test_update_product(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "",
                        "bewijs": "bewijs dat tekst wordt aangemaakt",
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
                        "bewijs": "proof that text gets created",
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
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(str(self.generiek_product.upn_label), data["upnLabel"])
        self.assertEqual(self.generiek_product.upn_uri, data["upnUri"])
        self.assertEqual(data["publicatieDatum"], str(NOW_DATE))
        self.assertEqual(data["productAanwezig"], 1)
        self.assertEqual(data["productValtOnder"], None)
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )
        self.assertEqual(data["locaties"], [])
        self.assertEqual(data["vertalingen"][0]["taal"], "nl")
        self.assertEqual(data["vertalingen"][0]["specifiekeTekst"], "")
        self.assertEqual(
            data["vertalingen"][0]["bewijs"], "bewijs dat tekst wordt aangemaakt"
        )
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
        self.assertEqual(
            data["vertalingen"][1]["bewijs"], "proof that text gets created"
        )
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

    def test_update_product_with_filled_in_translations(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "voorbeeld",
                        "bewijs": "voorbeeld",
                        "bezwaarEnBeroep": "voorbeeld",
                        "decentraleProcedureLink": "https://www.voorbeeld.nl",
                        "kostenEnBetaalmethoden": "voorbeeld",
                        "procedureBeschrijving": "voorbeeld",
                        "productTitelDecentraal": "voorbeeld",
                        "uitersteTermijn": "voorbeeld",
                        "vereisten": "voorbeeld",
                        "verwijzingLinks": [
                            {"label": "Test", "url": "https://www.voorbeeld.nl"},
                            {"label": "Test2", "url": "https://www.voorbeeld2.nl"},
                        ],
                        "wtdBijGeenReactie": "voorbeeld",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                    {
                        "taal": "en",
                        "specifiekeTekst": "example",
                        "bewijs": "example",
                        "bezwaarEnBeroep": "example",
                        "decentraleProcedureLink": "https://www.example.com",
                        "kostenEnBetaalmethoden": "example",
                        "procedureBeschrijving": "example",
                        "productTitelDecentraal": "example",
                        "uitersteTermijn": "example",
                        "vereisten": "example",
                        "verwijzingLinks": [
                            {"label": "Test", "url": "https://www.example.com"},
                            {"label": "Test2", "url": "https://www.example2.com"},
                        ],
                        "wtdBijGeenReactie": "example",
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "",
                    },
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(str(self.generiek_product.upn_label), data["upnLabel"])
        self.assertEqual(self.generiek_product.upn_uri, data["upnUri"])
        self.assertEqual(data["publicatieDatum"], str(NOW_DATE))
        self.assertEqual(data["productAanwezig"], 1)
        self.assertEqual(data["productValtOnder"], None)
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )
        self.assertEqual(data["locaties"], [])
        self.assertEqual(data["vertalingen"][0]["taal"], "nl")
        self.assertEqual(data["vertalingen"][0]["specifiekeTekst"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["bewijs"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["bezwaarEnBeroep"], "voorbeeld")
        self.assertEqual(
            data["vertalingen"][0]["decentraleProcedureLink"],
            "https://www.voorbeeld.nl",
        )
        self.assertEqual(data["vertalingen"][0]["kostenEnBetaalmethoden"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["procedureBeschrijving"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["productTitelDecentraal"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["uitersteTermijn"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["vereisten"], "voorbeeld")
        self.assertEqual(
            data["vertalingen"][0]["verwijzingLinks"],
            [
                {"label": "Test", "url": "https://www.voorbeeld.nl"},
                {"label": "Test2", "url": "https://www.voorbeeld2.nl"},
            ],
        )
        self.assertEqual(data["vertalingen"][0]["wtdBijGeenReactie"], "voorbeeld")
        self.assertEqual(data["vertalingen"][0]["productAanwezigToelichting"], "")
        self.assertEqual(data["vertalingen"][0]["productValtOnderToelichting"], "")

        self.assertEqual(data["vertalingen"][1]["taal"], "en")
        self.assertEqual(data["vertalingen"][1]["specifiekeTekst"], "example")
        self.assertEqual(data["vertalingen"][1]["bewijs"], "example")
        self.assertEqual(data["vertalingen"][1]["bezwaarEnBeroep"], "example")
        self.assertEqual(
            data["vertalingen"][1]["decentraleProcedureLink"], "https://www.example.com"
        )
        self.assertEqual(data["vertalingen"][1]["kostenEnBetaalmethoden"], "example")
        self.assertEqual(data["vertalingen"][1]["procedureBeschrijving"], "example")
        self.assertEqual(data["vertalingen"][1]["productTitelDecentraal"], "example")
        self.assertEqual(data["vertalingen"][1]["uitersteTermijn"], "example")
        self.assertEqual(data["vertalingen"][1]["vereisten"], "example")
        self.assertEqual(
            data["vertalingen"][1]["verwijzingLinks"],
            [
                {"label": "Test", "url": "https://www.example.com"},
                {"label": "Test2", "url": "https://www.example2.com"},
            ],
        )
        self.assertEqual(data["vertalingen"][1]["wtdBijGeenReactie"], "example")
        self.assertEqual(data["vertalingen"][1]["productAanwezigToelichting"], "")
        self.assertEqual(data["vertalingen"][1]["productValtOnderToelichting"], "")
        self.assertEqual(data["gerelateerdeProducten"], [])

    def test_update_product_with_one_translation(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
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
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_product_version(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        # update publicatieDatum to change the product first to a published item
        self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["versie"], 2)

    def test_update_product_version_with_create_endpoint(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "publicatieDatum": str(NOW_DATE),
                "vertalingen": [
                    {
                        "taal": "nl",
                        "specifiekeTekst": "generieke tekst om te kijken of hij update",
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
                        "specifiekeTekst": "generic text to see if it updates",
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
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["versie"], 1)

        self.assertEqual(str(self.generiek_product.upn_label), data["upnLabel"])
        self.assertEqual(self.generiek_product.upn_uri, data["upnUri"])
        self.assertEqual(data["publicatieDatum"], str(NOW_DATE))
        self.assertEqual(data["productAanwezig"], 1)
        self.assertEqual(data["productValtOnder"], None)
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )
        self.assertEqual(data["locaties"], [])
        self.assertEqual(data["vertalingen"][0]["taal"], "nl")
        self.assertEqual(
            data["vertalingen"][0]["specifiekeTekst"],
            "generieke tekst om te kijken of hij update",
        )
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
        self.assertEqual(
            data["vertalingen"][1]["specifiekeTekst"],
            "generic text to see if it updates",
        )
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

    def test_update_product_with_upn_pref_label(self):
        list_url = reverse("api:product-list")

        body = self.body
        body.pop("upnUri")

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["upnLabel"], "setup")
        self.assertEqual(create_data["upnUri"], "https://www.setup.com")

    def test_update_product_with_upn_uri(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body({"publicatieDatum": None})
        body.pop("upnUri")

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["upnLabel"], "setup")
        self.assertEqual(create_data["upnUri"], "https://www.setup.com")

    def test_update_product_without_upn(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body({"publicatieDatum": str(NOW_DATE)})

        body = self.body
        body.pop("upnLabel")
        body.pop("upnUri")

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_with_product_aanwezig_false_with_toelichting(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "productAanwezig": 0,
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
                        "productAanwezigToelichting": "Text",
                        "productValtOnderToelichting": "",
                    },
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertFalse(create_data["productAanwezig"])
        self.assertEqual(
            create_data["vertalingen"][0]["productAanwezigToelichting"], "Tekst"
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productAanwezigToelichting"], "Text"
        )

    def test_update_product_with_product_aanwezig_false_without_toelichting(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "productAanwezig": 0,
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_with_product_valt_onder_label_with_toelichting(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "productValtOnder": {
                    "upnLabel": self.second_test_product.generiek_product.upn.upn_label,
                },
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
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "Text",
                    },
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertTrue(create_data["productValtOnder"])
        self.assertEqual(
            create_data["vertalingen"][0]["productValtOnderToelichting"], "Tekst"
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productValtOnderToelichting"], "Text"
        )

    def test_update_product_with_product_valt_onder_uri_with_toelichting(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "productValtOnder": {
                    "upnUri": self.second_test_product.generiek_product.upn.upn_uri,
                },
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
                        "productAanwezigToelichting": "",
                        "productValtOnderToelichting": "Text",
                    },
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertTrue(create_data["productValtOnder"])
        self.assertEqual(
            create_data["vertalingen"][0]["productValtOnderToelichting"], "Tekst"
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productValtOnderToelichting"], "Text"
        )

    def test_update_product_with_product_valt_onder_without_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.test_update_product_with_product_valt_onder_without_toelichting.com",
            owms_pref_label="test_update_product_with_product_valt_onder_without_toelichting",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            naam="test_update_product_with_product_valt_onder_without_toelichting",
            organisatie=organisatie,
            lokale_overheid=lokale_overheid,
        )
        second_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            bevoegde_organisatie=bevoegde_organisatie,
            catalogus=self.test_catalog,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(
            product=second_product, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "productValtOnder": {
                    "upnLabel": second_product.generiek_product.upn.upn_label,
                    "upnUri": second_product.generiek_product.upn.upn_uri,
                },
            }
        )

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_with_verantwoordelijke_organisatie_pref_label(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "organisatie",
                }
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )

    def test_update_product_with_verantwoordelijke_organisatie_identifier(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "verantwoordelijkeOrganisatie": {
                    "owmsIdentifier": "https://www.organisatie.com",
                }
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )

    def test_update_product_with_different_verantwoordelijke_organisatie(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "set up",
                    "owmsIdentifier": "https://www.setup.com",
                }
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "set up"
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

    def test_update_product_with_bevoegde_organisatie_naam(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "bevoegdeOrganisatie": {
                    "naam": self.bevoegde_organisatie.naam,
                }
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["naam"],
            self.bevoegde_organisatie.naam,
        )
        self.assertEqual(create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

    def test_update_product_with_bevoegde_organisatie_pref_label(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "bevoegdeOrganisatie": {
                    "owmsPrefLabel": self.organisatie.owms_pref_label,
                }
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["naam"],
            self.bevoegde_organisatie.naam,
        )
        self.assertEqual(create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

    def test_update_product_with_bevoegde_organisatie_identifier(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "bevoegdeOrganisatie": {
                    "owmsIdentifier": self.organisatie.owms_identifier,
                },
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["naam"],
            self.bevoegde_organisatie.naam,
        )
        self.assertEqual(create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

    def test_update_product_with_no_bevoegde_organisatie(self):
        list_url = reverse("api:product-list")

        body = self.body

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )

    def test_update_product_with_locaties_uuid(self):
        locatie1, locatie2, locatie3 = LocatieFactory.create_batch(
            3, lokale_overheid=self.test_lokale_overheid
        )

        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "locaties": [
                    {"uuid": str(locatie1.uuid)},
                    {"uuid": str(locatie2.uuid)},
                    {"uuid": str(locatie3.uuid)},
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["locaties"]), 3)

        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie1.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie1.naam)

        self.assertEqual(create_data["locaties"][1]["uuid"], str(locatie2.uuid))
        self.assertEqual(create_data["locaties"][1]["naam"], locatie2.naam)

        self.assertEqual(create_data["locaties"][2]["uuid"], str(locatie3.uuid))
        self.assertEqual(create_data["locaties"][2]["naam"], locatie3.naam)

    def test_update_product_with_locaties_naam(self):
        locatie1, locatie2, locatie3 = LocatieFactory.create_batch(
            3, lokale_overheid=self.test_lokale_overheid
        )

        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "locaties": [
                    {"naam": locatie1.naam},
                    {"naam": locatie2.naam},
                    {"naam": locatie3.naam},
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["locaties"]), 3)

        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie1.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie1.naam)

        self.assertEqual(create_data["locaties"][1]["uuid"], str(locatie2.uuid))
        self.assertEqual(create_data["locaties"][1]["naam"], locatie2.naam)

        self.assertEqual(create_data["locaties"][2]["uuid"], str(locatie3.uuid))
        self.assertEqual(create_data["locaties"][2]["naam"], locatie3.naam)

    def test_update_product_with_gerelateerde_producten_upn_label(self):
        third_upn = UniformeProductnaamFactory.create(
            upn_label="third",
            upn_uri="https://www.third.com",
        )
        third_generiek_product = GeneriekProductFactory.create(
            upn=third_upn,
            doelgroep="eu-burger",
        )
        third_referentie_product = ReferentieProductFactory.create(
            generiek_product=third_generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
            product_aanwezig=True,
        )
        third_referentie_product_versie = ProductVersieFactory.create(
            product=third_referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=third_referentie_product_versie
        )

        product3 = SpecifiekProductFactory.create(
            generiek_product=third_generiek_product,
            referentie_product=third_referentie_product,
            catalogus=self.catalogus,
            bevoegde_organisatie=self.bevoegde_organisatie,
            product_aanwezig=True,
        )
        product_versie3 = ProductVersieFactory.create(
            product=product3, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie3)

        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "verantwoordelijkeOrganisatie": {
                    "owmsLabel": "set up",
                    "owmsIdentifier": "https://www.setup.com",
                },
                "gerelateerdeProducten": [
                    {"upnLabel": self.seccond_product.generiek_product.upn.upn_label},
                    {"upnLabel": product3.generiek_product.upn.upn_label},
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["gerelateerdeProducten"]), 2)

        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnLabel"],
            self.seccond_product.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            self.seccond_product.generiek_product.upn.upn_uri,
        )

        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnLabel"],
            product3.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnUri"],
            product3.generiek_product.upn.upn_uri,
        )

    def test_update_product_with_gerelateerde_producten_upn_uri(self):
        third_upn = UniformeProductnaamFactory.create(
            upn_label="third",
            upn_uri="https://www.third.com",
        )
        third_generiek_product = GeneriekProductFactory.create(
            upn=third_upn,
            doelgroep="eu-burger",
        )
        third_referentie_product = ReferentieProductFactory.create(
            generiek_product=third_generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
            product_aanwezig=True,
        )
        third_referentie_product_versie = ProductVersieFactory.create(
            product=third_referentie_product
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=third_referentie_product_versie
        )

        product3 = SpecifiekProductFactory.create(
            generiek_product=third_generiek_product,
            referentie_product=third_referentie_product,
            catalogus=self.catalogus,
            bevoegde_organisatie=self.bevoegde_organisatie,
            product_aanwezig=True,
        )
        product_versie3 = ProductVersieFactory.create(
            product=product3, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie3)

        list_url = reverse("api:product-list")

        body = self.get_product_post_body(
            {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "verantwoordelijkeOrganisatie": {
                    "owmsLabel": "set up",
                    "owmsIdentifier": "https://www.setup.com",
                },
                "gerelateerdeProducten": [
                    {"upnUri": self.seccond_product.generiek_product.upn.upn_uri},
                    {"upnUri": product3.generiek_product.upn.upn_uri},
                ],
            }
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["gerelateerdeProducten"]), 2)

        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnLabel"],
            self.seccond_product.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            self.seccond_product.generiek_product.upn.upn_uri,
        )

        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnLabel"],
            product3.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnUri"],
            product3.generiek_product.upn.upn_uri,
        )

    def test_update_product_with_invalid_doelgroep(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body({"doelgroep": "test1234"})

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_with_wrong_doelgroep(self):
        list_url = reverse("api:product-list")

        body = self.get_product_post_body({"doelgroep": "eu-bedrijf"})

        headers = {"HTTP_AUTHORIZATION": f"Token {self.test_token_authorization.token}"}

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

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

    @freeze_time(NOW_DATE)
    def test_list_product_concept(self):
        product = ReferentieProductFactory.create()
        ReferentieProductVersieFactory.create_batch(
            3, publicatie_datum=PAST_DATE, product=product
        )
        concept = ReferentieProductVersieFactory.create(
            publicatie_datum=None, product=product
        )

        response = self.client.get(
            reverse("api:product-concept-list", args=[product.uuid])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(1, len(data))
        self.assertEqual(concept.versie, data[0]["versie"])

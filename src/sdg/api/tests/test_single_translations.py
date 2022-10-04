import json

from django.test import override_settings

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
    SpecifiekProductFactory,
)


@override_settings(SDG_API_WHITELISTING_ENABLED=False)
class SingleProductenTests(APITestCase):
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
        self.locatie1, self.locatie2, self.locatie3 = LocatieFactory.create_batch(
            3, lokale_overheid=self.lokale_overheid
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
            publicatie_datum=NOW_DATE,
        )
        self.second_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.second_product_versie
        )

    def test_single_product_withBody(self):
        list_url = reverse("api:product-single-list", args=[str(self.product.uuid)])

        body = {
            "productAanwezig": True,
            "productValtOnder": {"upnUri": "https://www.second-setup.com"},
            "locaties": [
                {"naam": self.locatie1.naam},
                {"naam": self.locatie2.naam},
                {"naam": self.locatie3.naam},
            ],
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["productAanwezig"], 1)
        self.assertEqual(
            data["productValtOnder"]["upnUri"],
            str(self.seccond_product.generiek_product.upn_uri),
        )
        self.assertEqual(data["locaties"][0]["naam"], self.locatie1.naam)
        self.assertEqual(data["locaties"][1]["naam"], self.locatie2.naam)
        self.assertEqual(data["locaties"][2]["naam"], self.locatie3.naam)

    def test_single_product_without_body(self):
        list_url = reverse("api:product-single-list", args=[str(self.product.uuid)])

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(
            data["invalidParams"],
            [
                {
                    "name": "productAanwezig",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
                {
                    "name": "productValtOnder",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
                {
                    "name": "locaties",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            ],
        )

    def test_single_product_vertaling_with_body(self):
        list_url = reverse(
            "api:product-single-vertalingen-list", args=[str(self.product.uuid)]
        )

        body = {
            "taal": "nl",
            "titel": "test",
            "tekst": "test",
            "links": [
                {"label": "test1", "url": "https://www.test1.com"},
                {"label": "test2", "url": "https://www.test2.com"},
            ],
            "procedureBeschrijving": "test",
            "bewijs": "test",
            "vereisten": "test",
            "bezwaarEnBeroep": "test",
            "kostenEnBetaalmethoden": "test",
            "uitersteTermijn": "test",
            "wtdBijGeenReactie": "test",
            "procedureLink": {"label": "test", "url": "http://test.com"},
            "productAanwezigToelichting": "",
            "productValtOnderToelichting": "",
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["taal"], "nl")
        self.assertEqual(data["tekst"], "test")
        self.assertEqual(data["titel"], "test")
        self.assertEqual(
            data["links"],
            [
                {"label": "test1", "url": "https://www.test1.com"},
                {"label": "test2", "url": "https://www.test2.com"},
            ],
        )
        self.assertEqual(data["procedureBeschrijving"], "test")
        self.assertEqual(data["bewijs"], "test")
        self.assertEqual(data["vereisten"], "test")
        self.assertEqual(data["bezwaarEnBeroep"], "test")
        self.assertEqual(data["kostenEnBetaalmethoden"], "test")
        self.assertEqual(data["uitersteTermijn"], "test")
        self.assertEqual(data["wtdBijGeenReactie"], "test")
        self.assertEqual(
            data["procedureLink"],
            {"label": "test", "url": "http://test.com"},
        )
        self.assertEqual(data["productAanwezigToelichting"], "")
        self.assertEqual(data["productValtOnderToelichting"], "")

    def test_single_product_vertaling_without_body(self):
        list_url = reverse(
            "api:product-single-vertalingen-list", args=[str(self.product.uuid)]
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(
            data["invalidParams"],
            [
                {
                    "name": "taal",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                }
            ],
        )

    def test_single_product_vertaling_toelichting_wrongly_filled_in(self):
        list_url = reverse("api:product-single-list", args=[str(self.product.uuid)])

        generic_single_body = {
            "productAanwezig": True,
            "productValtOnder": None,
            "locaties": [],
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        self.client.post(
            list_url,
            data=json.dumps(generic_single_body),
            content_type="application/json",
            **headers,
        )

        list_url = reverse(
            "api:product-single-vertalingen-list", args=[str(self.product.uuid)]
        )

        with self.subTest("productAanwezigToelichting"):

            body = {
                "taal": "nl",
                "productAanwezigToelichting": "test",
                "productValtOnderToelichting": "",
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = response.json()
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "productAanwezigToelichting",
                        "code": "invalid",
                        "reason": "ProductAanwezigToelichting moet niet ingevult zijn zolang productAanwezig op 'true' staat.",
                    }
                ],
            )

        with self.subTest("productValtOnderToelichting"):

            body = {
                "taal": "nl",
                "productAanwezigToelichting": "",
                "productValtOnderToelichting": "test",
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = response.json()
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "productValtOnderToelichting",
                        "code": "invalid",
                        "reason": "ProductValtOnderToelichting moet niet ingevult zijn zolang productValtOnder op 'null' staat.",
                    }
                ],
            )

    def test_single_product_vertaling_toelichting_wrongly_forgotten(self):
        list_url = reverse("api:product-single-list", args=[str(self.product.uuid)])

        generic_single_body = {
            "productAanwezig": False,
            "productValtOnder": {"upnUri": "https://www.second-setup.com"},
            "locaties": [],
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        self.client.post(
            list_url,
            data=json.dumps(generic_single_body),
            content_type="application/json",
            **headers,
        )

        list_url = reverse(
            "api:product-single-vertalingen-list", args=[str(self.product.uuid)]
        )

        with self.subTest("productAanwezigToelichting"):

            body = {
                "taal": "nl",
                "productAanwezigToelichting": "",
                "productValtOnderToelichting": "test",
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = response.json()
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "productAanwezigToelichting",
                        "code": "invalid",
                        "reason": "ProductAanwezigToelichting moet ingevult zijn zolang productAanwezig op 'false' staat.",
                    }
                ],
            )

        with self.subTest("productValtOnderToelichting"):

            body = {
                "taal": "nl",
                "productAanwezigToelichting": "test",
                "productValtOnderToelichting": "",
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = response.json()
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "productValtOnderToelichting",
                        "code": "invalid",
                        "reason": "ProductValtOnderToelichting moet ingevult zijn zolang productValtOnder niet op 'null' staat.",
                    }
                ],
            )

    def test_single_product_vertaling_on_published_product(self):
        list_url = reverse(
            "api:product-single-vertalingen-list", args=[str(self.seccond_product.uuid)]
        )

        body = {
            "taal": "nl",
            "titel": "test",
            "tekst": "test",
            "links": [
                {"label": "test1", "url": "https://www.test1.com"},
                {"label": "test2", "url": "https://www.test2.com"},
            ],
            "procedureBeschrijving": "test",
            "bewijs": "test",
            "vereisten": "test",
            "bezwaarEnBeroep": "test",
            "kostenEnBetaalmethoden": "test",
            "uitersteTermijn": "test",
            "wtdBijGeenReactie": "test",
            "procedureLink": {"label": "test", "url": "http://test.com"},
            "productAanwezigToelichting": "",
            "productValtOnderToelichting": "",
        }

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["invalidParams"],
            [
                {
                    "name": "",
                    "code": "invalid",
                    "reason": "Het product dat u probeert aan tepassen is geen concept.",
                }
            ],
        )

    def test_single_product_publish(self):
        list_url = reverse("api:product-single-publish", args=[str(self.product.uuid)])

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_product_publish_already_published_product(self):
        list_url = reverse(
            "api:product-single-publish", args=[str(self.seccond_product.uuid)]
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["invalidParams"],
            [
                {
                    "name": "",
                    "code": "invalid",
                    "reason": "Een gepubliceerde product kan niet nog een keer gepubliseerd worden.",
                }
            ],
        )

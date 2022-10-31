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
            owms_identifier="https://www.single_producten_tests.com",
            owms_pref_label="single_producten_tests",
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
            naam="single_producten_tests_catalogus",
        )
        self.upn = UniformeProductnaamFactory.create(
            upn_label="single_producten_tests_first_product",
            upn_uri="https://www.single_producten_tests_first_product.com",
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
            product=self.referentie_product, versie=1
        )
        self.referentie_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.referentie_product_versie
        )

        self.second_upn = UniformeProductnaamFactory.create(
            upn_label="single-producten-tests-second-product",
            upn_uri="https://www.single-producten-tests-second-product.com",
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
            product=self.second_referentie_product, versie=1
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=self.second_referentie_product_versie
        )

        self.future_published_upn = UniformeProductnaamFactory.create(
            upn_label="future",
            upn_uri="https://www.future.com",
        )
        self.future_published_generiek_product = GeneriekProductFactory.create(
            upn=self.future_published_upn,
            doelgroep="eu-burger",
        )
        self.future_published_referentie_product = ReferentieProductFactory.create(
            generiek_product=self.future_published_generiek_product,
            referentie_product=None,
            catalogus=self.referentie_catalogus,
            bevoegde_organisatie=self.referentie_bevoegde_organisatie,
            product_aanwezig=True,
        )
        self.future_published_referentie_product_versie = ProductVersieFactory.create(
            product=self.future_published_referentie_product, versie=1
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=self.future_published_referentie_product_versie
        )

        self.organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.single_producten_tests_first_organisatie.com",
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
            naam="single_producten_tests_first_catalogus",
        )
        self.product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=self.catalogus,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie,
        )
        self.product_versie = ProductVersieFactory.create(
            product=self.product, publicatie_datum=None, versie=1
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
            product=self.seccond_product, publicatie_datum=NOW_DATE, versie=1
        )
        self.second_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.second_product_versie
        )

        self.future_published_product = SpecifiekProductFactory.create(
            generiek_product=self.future_published_generiek_product,
            referentie_product=self.future_published_referentie_product,
            catalogus=self.catalogus,
            product_aanwezig=True,
            bevoegde_organisatie=self.bevoegde_organisatie,
        )
        self.future_published_product_versie = ProductVersieFactory.create(
            product=self.future_published_product,
            publicatie_datum=FUTURE_DATE,
            versie=1,
        )
        self.future_published_localized_products = LocalizedProductFactory.create_batch(
            2, product_versie=self.future_published_product_versie
        )

    def test_single_product_withBody(self):
        list_url = reverse(
            "api:versies-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
            },
        )

        body = {
            "productAanwezig": True,
            "productValtOnder": {
                "upnUri": "https://www.single-producten-tests-second-product.com"
            },
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
        list_url = reverse(
            "api:versies-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
            },
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

    def test_single_future_published(self):
        list_url = reverse(
            "api:versies-create-list",
            kwargs={
                "versies_uuid": str(self.future_published_product.uuid),
                "versie": str(self.future_published_product_versie.versie),
            },
        )

        body = {
            "productAanwezig": True,
            "productValtOnder": {
                "upnUri": "https://www.single-producten-tests-second-product.com"
            },
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

    def test_single_product_vertaling_with_body(self):
        list_url = reverse(
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
                "taal": "nl",
            },
        )

        body = {
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
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
                "taal": "nl",
            },
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_single_product_vertaling_future_published(self):
        list_url = reverse(
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.future_published_product.uuid),
                "versie": str(self.future_published_product_versie.versie),
                "taal": "nl",
            },
        )

        body = {
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

    def test_single_product_vertaling_toelichting_wrongly_filled_in(self):
        list_url = reverse(
            "api:versies-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
            },
        )

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
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
                "taal": "nl",
            },
        )

        with self.subTest("productAanwezigToelichting"):

            body = {
                "productAanwezigToelichting": "test",
                "productValtOnderToelichting": "",
            }

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
                "productAanwezigToelichting": "",
                "productValtOnderToelichting": "test",
            }

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
        list_url = reverse(
            "api:versies-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
            },
        )

        generic_single_body = {
            "productAanwezig": False,
            "productValtOnder": {
                "upnUri": "https://www.single-producten-tests-second-product.com"
            },
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
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
                "taal": "nl",
            },
        )

        with self.subTest("productAanwezigToelichting"):

            body = {
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
            "api:versies-vertalingen-create-list",
            kwargs={
                "versies_uuid": str(self.seccond_product.uuid),
                "versie": str(self.second_product_versie.versie),
                "taal": "nl",
            },
        )

        body = {
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
        list_url = reverse(
            "api:versies-create-publish",
            kwargs={
                "versies_uuid": str(self.product.uuid),
                "versie": str(self.product_versie.versie),
            },
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_single_product_publish_already_published_product(self):
        list_url = reverse(
            "api:versies-create-publish",
            kwargs={
                "versies_uuid": str(self.seccond_product.uuid),
                "versie": str(self.second_product_versie.versie),
            },
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

    def test_single_product_with_not_correctly_filled_out_product(self):
        with self.subTest("wrongly_filled_out_productAanwezig"):
            list_url = reverse(
                "api:versies-create-list",
                kwargs={
                    "versies_uuid": str(self.product.uuid),
                    "versie": str(self.product_versie.versie),
                },
            )

            body = {
                "productAanwezig": False,
                "productValtOnder": None,
                "locaties": [],
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            list_url = reverse(
                "api:versies-create-publish",
                kwargs={
                    "versies_uuid": str(self.product.uuid),
                    "versie": str(self.product_versie.versie),
                },
            )

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                content_type="application/json",
                **headers,
            )
            data = response.json()

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "",
                        "code": "invalid",
                        "reason": "ProductAanwezigToelichting moet ingevult zijn zolang productAanwezig op 'false' staat.",
                    }
                ],
            )

        with self.subTest("wrongly_filled_out_productValtOnder"):
            list_url = reverse(
                "api:versies-create-list",
                kwargs={
                    "versies_uuid": str(self.product.uuid),
                    "versie": str(self.product_versie.versie),
                },
            )

            body = {
                "productAanwezig": True,
                "productValtOnder": {
                    "upnUri": "https://www.single-producten-tests-second-product.com"
                },
                "locaties": [],
            }

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                list_url,
                data=json.dumps(body),
                content_type="application/json",
                **headers,
            )

            print(response.json())

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            list_url = reverse(
                "api:versies-create-publish",
                kwargs={
                    "versies_uuid": str(self.product.uuid),
                    "versie": str(self.product_versie.versie),
                },
            )

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response2 = self.client.post(
                list_url,
                content_type="application/json",
                **headers,
            )
            data = response2.json()
            self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "",
                        "code": "invalid",
                        "reason": "ProductValtOnderToelichting moet ingevult zijn zolang productValtOnder niet op 'null' staat.",
                    }
                ],
            )

        with self.subTest("wrongly_filled_out_productAanwezigToelichting"):
            upn = UniformeProductnaamFactory.create(
                upn_label="error",
                upn_uri="https://www.error.com",
            )
            generiek_product = GeneriekProductFactory.create(
                upn=upn,
                doelgroep="eu-burger",
            )
            referentie_product = ReferentieProductFactory.create(
                generiek_product=generiek_product,
                referentie_product=None,
                catalogus=self.referentie_catalogus,
                bevoegde_organisatie=self.referentie_bevoegde_organisatie,
                product_aanwezig=True,
            )
            ProductVersieFactory.create(product=referentie_product, versie=1)

            product = SpecifiekProductFactory.create(
                generiek_product=generiek_product,
                referentie_product=referentie_product,
                catalogus=self.catalogus,
                product_aanwezig=True,
                product_valt_onder=None,
                bevoegde_organisatie=self.bevoegde_organisatie,
            )
            product_versie = ProductVersieFactory.create(
                product=product, publicatie_datum=FUTURE_DATE, versie=1
            )
            LocalizedProductFactory.create_batch(
                2, product_versie=product_versie, product_aanwezig_toelichting="error"
            )

            url = reverse(
                "api:versies-create-publish",
                kwargs={
                    "versies_uuid": str(product.uuid),
                    "versie": str(product_versie.versie),
                },
            )

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                url,
                content_type="application/json",
                **headers,
            )
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "",
                        "code": "invalid",
                        "reason": "ProductAanwezigToelichting moet niet ingevult zijn zolang productAanwezig op 'true' staat.",
                    }
                ],
            )

        with self.subTest("wrongly_filled_out_productValtOnderToelichting"):
            upn = UniformeProductnaamFactory.create(
                upn_label="error2",
                upn_uri="https://www.error2.com",
            )
            generiek_product = GeneriekProductFactory.create(
                upn=upn,
                doelgroep="eu-burger",
            )
            referentie_product = ReferentieProductFactory.create(
                generiek_product=generiek_product,
                referentie_product=None,
                catalogus=self.referentie_catalogus,
                bevoegde_organisatie=self.referentie_bevoegde_organisatie,
                product_aanwezig=True,
            )
            ProductVersieFactory.create(product=referentie_product, versie=1)

            product = SpecifiekProductFactory.create(
                generiek_product=generiek_product,
                referentie_product=referentie_product,
                catalogus=self.catalogus,
                product_aanwezig=True,
                product_valt_onder=None,
                bevoegde_organisatie=self.bevoegde_organisatie,
            )
            product_versie = ProductVersieFactory.create(
                product=product, publicatie_datum=FUTURE_DATE, versie=1
            )
            LocalizedProductFactory.create_batch(
                2, product_versie=product_versie, product_valt_onder_toelichting="error"
            )

            url = reverse(
                "api:versies-create-publish",
                kwargs={
                    "versies_uuid": str(product.uuid),
                    "versie": str(product_versie.versie),
                },
            )

            headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

            response = self.client.post(
                url,
                content_type="application/json",
                **headers,
            )
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                data["invalidParams"],
                [
                    {
                        "name": "",
                        "code": "invalid",
                        "reason": "ProductValtOnderToelichting moet niet ingevult zijn zolang productValtOnder op 'null' staat.",
                    }
                ],
            )

    def test_single_product_publish_future_date(self):
        list_url = reverse(
            "api:versies-create-publish",
            kwargs={
                "versies_uuid": str(self.future_published_product.uuid),
                "versie": str(self.future_published_product_versie.versie),
            },
        )

        headers = {"HTTP_AUTHORIZATION": f"Token {self.token_authorization.token}"}

        response = self.client.post(
            list_url,
            content_type="application/json",
            **headers,
            data=json.dumps({"publicatieDatum": str(NOW_DATE)}),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

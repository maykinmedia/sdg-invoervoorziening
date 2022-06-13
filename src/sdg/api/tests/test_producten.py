import json

from freezegun import freeze_time
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
from sdg.producten.tests.constants import NOW_DATE, PAST_DATE
from sdg.producten.tests.factories.localized import LocalizedProductFactory
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductVersieFactory,
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductFactory,
)


class ProductenTests(APITestCase):
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

    def test_list_producten(self):
        list_url = reverse("api:product-list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(3, len(data))

    def test_retrieve_product_by_uuid(self):
        detail_url = reverse("api:product-detail", args=[self.product.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(str(self.product.uuid), data["uuid"])

    def test_creating_product(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": str(NOW_DATE),
            "productAanwezig": 1,
            "productValtOnder": None,
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

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_new_product_version(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie",
        )
        product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        product_versie = ProductVersieFactory.create(
            product=product, publicatie_datum=str(NOW_DATE), versie=1
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": str(NOW_DATE),
            "productAanwezig": 1,
            "productValtOnder": None,
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

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["versie"], 2)

    def test_update_product_version_with_create_endpoint(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie",
        )
        product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        product_versie = ProductVersieFactory.create(
            product=product,
            publicatie_datum=None,
            versie=1,
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": str(NOW_DATE),
            "productAanwezig": 1,
            "productValtOnder": None,
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

        response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["versie"], 1)

    def test_updating_product(self):
        detail_url = reverse("api:product-detail", args=[self.product.uuid])

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": str(NOW_DATE),
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
        self.assertEqual(data["publicatieDatum"], str(NOW_DATE))
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

    def test_updating_published_product(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie",
        )
        product = SpecifiekProductFactory.create(
            generiek_product=self.generiek_product,
            referentie_product=self.referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        product_versie = ProductVersieFactory.create(
            product=product,
            publicatie_datum=str(NOW_DATE),
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie)

        detail_url = reverse("api:product-detail", args=[product.uuid])

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": str(NOW_DATE),
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_product_with_upn_pref_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()
        self.assertEqual(create_data["upnLabel"], "setup")
        self.assertEqual(create_data["upnUri"], "https://www.setup.com")

        with self.subTest("test_updating_product_with_upn_label"):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "publicatieDatum": str(NOW_DATE),
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
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
        ProductenCatalogusFactory.create(
            lokale_overheid=self.lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "referentie",
                "owmsIdentifier": "https://www.referentie.com",
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
                "publicatieDatum": str(NOW_DATE),
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "referentie",
                    "owmsIdentifier": "https://www.referentie.com",
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

    def test_creating_product_without_upn(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest("test_updating_product_without_upn"):
            detail_url = reverse("api:product-detail", args=[str(self.product.uuid)])

            body = {
                "publicatieDatum": str(NOW_DATE),
                "productAanwezig": 1,
                "productValtOnder": None,
                "verantwoordelijkeOrganisatie": {
                    "owmsPrefLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
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

            self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_product_with_product_aanwezig_false_with_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 0,
            "productValtOnder": None,
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
        self.assertEqual(
            create_data["vertalingen"][0]["productAanwezigToelichting"], "Tekst"
        )
        self.assertEqual(
            create_data["vertalingen"][1]["productAanwezigToelichting"], "Text"
        )

        with self.subTest(
            "test_update_product_with_product_aanwezig_false_with_toelichting"
        ):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 0,
                "productValtOnder": None,
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
                        "productAanwezigToelichting": "Upgedate Tekst",
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
                        "productAanwezigToelichting": "Updated Text",
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

            self.assertFalse(update_data["productAanwezig"])
            self.assertEqual(
                update_data["vertalingen"][0]["productAanwezigToelichting"],
                "Upgedate Tekst",
            )
            self.assertEqual(
                update_data["vertalingen"][1]["productAanwezigToelichting"],
                "Updated Text",
            )

    def test_creating_product_with_product_aanwezig_false_without_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 0,
            "productValtOnder": None,
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest(
            "test_update_product_with_product_aanwezig_false_without_toelichting"
        ):
            detail_url = reverse("api:product-detail", args=[str(self.product.uuid)])

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 0,
                "productValtOnder": None,
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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_product_with_product_valt_onder_label_with_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(
            product=second_product, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": {
                "upnLabel": second_product.generiek_product.upn.upn_label,
            },
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
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
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

        with self.subTest(
            "test_update_product_with_product_valt_onder_label_with_toelichting"
        ):
            detail_url = reverse(
                "api:product-detail", args=[create_response.json()["uuid"]]
            )

            body = {
                "upnLabel": self.generiek_product.upn.upn_label,
                "upnUri": self.generiek_product.upn.upn_uri,
                "publicatieDatum": None,
                "productAanwezig": 1,
                "productValtOnder": {
                    "upnLabel": second_product.generiek_product.upn.upn_label,
                },
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
                        "productValtOnderToelichting": "Upgedate Tekst",
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
                        "productValtOnderToelichting": "Updated Text",
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

            self.assertTrue(update_data["productValtOnder"])
            self.assertEqual(
                update_data["vertalingen"][0]["productValtOnderToelichting"],
                "Upgedate Tekst",
            )
            self.assertEqual(
                update_data["vertalingen"][1]["productValtOnderToelichting"],
                "Updated Text",
            )

    def test_creating_product_with_product_valt_onder_uri_with_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(
            product=second_product, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=second_product_versie)

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": {
                "upnUri": second_product.generiek_product.upn.upn_uri,
            },
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
            "gerelateerdeProducten": [],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
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

    def test_creating_product_with_product_valt_onder_without_toelichting(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        second_product = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=catalogus,
            product_aanwezig=True,
        )
        second_product_versie = ProductVersieFactory.create(
            product=second_product, publicatie_datum=None
        )
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest(
            "test_update_product_with_product_valt_onder_without_toelichting"
        ):
            detail_url = reverse("api:product-detail", args=[str(self.product.uuid)])

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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_verantwoordelijke_organisatie_pref_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "organisatie",
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
            create_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"], "organisatie"
        )
        self.assertEqual(
            create_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
            "https://www.organisatie.com",
        )

        with self.subTest(
            "test_update_product_with_verantwoordelijke_organisatie_pref_label"
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
                    "owmsPrefLabel": "organisatie",
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
                update_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
                "organisatie",
            )
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
                "https://www.organisatie.com",
            )

    def test_create_product_with_verantwoordelijke_organisatie_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
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

        with self.subTest(
            "test_update_product_with_verantwoordelijke_organisatie_identifier"
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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsPrefLabel"],
                "organisatie",
            )
            self.assertEqual(
                update_data["verantwoordelijkeOrganisatie"]["owmsIdentifier"],
                "https://www.organisatie.com",
            )

    def test_create_product_with_bevoegde_organisatie_pref_label(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "organisatie",
                "owmsIdentifier": "https://www.organisatie.com",
            },
            "bevoegdeOrganisatie": {
                "owmsPrefLabel": self.organisatie.owms_pref_label,
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

        self.assertEqual(create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

        with self.subTest("test_update_product_with_bevoegde_organisatie_pref_label"):
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
                    "owmsPrefLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
                },
                "bevoegdeOrganisatie": {
                    "owmsPrefLabel": self.organisatie.owms_pref_label,
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
                update_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
                "set up",
            )
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsIdentifier"],
                "https://www.setup.com",
            )

    def test_create_product_with_bevoegde_organisatie_identifier(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=None,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsPrefLabel": "organisatie",
                "owmsIdentifier": "https://www.organisatie.com",
            },
            "bevoegdeOrganisatie": {
                "owmsIdentifier": self.organisatie.owms_identifier,
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

        self.assertEqual(create_data["bevoegdeOrganisatie"]["owmsPrefLabel"], "set up")
        self.assertEqual(
            create_data["bevoegdeOrganisatie"]["owmsIdentifier"],
            "https://www.setup.com",
        )

        with self.subTest("test_update_product_with_bevoegde_organisatie_identifier"):
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
                    "owmsPrefLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
                },
                "bevoegdeOrganisatie": {
                    "owmsIdentifier": self.organisatie.owms_identifier,
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
                update_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
                "set up",
            )
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsIdentifier"],
                "https://www.setup.com",
            )

    def test_create_product_with_no_bevoegde_organisatie(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=organisatie,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsLabel": "organisatie",
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

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
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

        with self.subTest("test_update_product_with_no_bevoegde_organisatie"):
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
                    "owmsLabel": "organisatie",
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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsPrefLabel"],
                "organisatie",
            )
            self.assertEqual(
                update_data["bevoegdeOrganisatie"]["owmsIdentifier"],
                "https://www.organisatie.com",
            )

    def test_create_product_with_locaties_uuid(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=organisatie,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )
        locatie1, locatie2, locatie3 = LocatieFactory.create_batch(
            3, lokale_overheid=lokale_overheid
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsLabel": "organisatie",
                "owmsIdentifier": "https://www.organisatie.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [
                {"uuid": str(locatie1.uuid)},
                {"uuid": str(locatie2.uuid)},
                {"uuid": str(locatie3.uuid)},
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

        self.assertEqual(len(create_data["locaties"]), 3)

        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie1.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie1.naam)

        self.assertEqual(create_data["locaties"][1]["uuid"], str(locatie2.uuid))
        self.assertEqual(create_data["locaties"][1]["naam"], locatie2.naam)

        self.assertEqual(create_data["locaties"][2]["uuid"], str(locatie3.uuid))
        self.assertEqual(create_data["locaties"][2]["naam"], locatie3.naam)

        with self.subTest("test_update_product_with_locaties_uuid"):
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
                    "owmsLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [
                    {"uuid": str(locatie1.uuid)},
                    {"uuid": str(locatie2.uuid)},
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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(len(update_data["locaties"]), 2)

            self.assertEqual(update_data["locaties"][0]["uuid"], str(locatie1.uuid))
            self.assertEqual(update_data["locaties"][0]["naam"], locatie1.naam)

            self.assertEqual(update_data["locaties"][1]["uuid"], str(locatie2.uuid))
            self.assertEqual(update_data["locaties"][1]["naam"], locatie2.naam)

    def test_create_product_with_locaties_naam(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.organisatie.com",
            owms_pref_label="organisatie",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
            contact_telefoonnummer="123456789",
        )
        BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie=organisatie,
            naam="organisatie",
        )
        ProductenCatalogusFactory.create(
            lokale_overheid=lokale_overheid,
            is_referentie_catalogus=False,
            is_default_catalogus=True,
            naam="organisatie_catalog",
        )
        locatie1, locatie2, locatie3 = LocatieFactory.create_batch(
            3, lokale_overheid=lokale_overheid
        )

        list_url = reverse("api:product-list")

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsLabel": "organisatie",
                "owmsIdentifier": "https://www.organisatie.com",
            },
            "bevoegdeOrganisatie": None,
            "locaties": [
                {"naam": locatie1.naam},
                {"naam": locatie2.naam},
                {"naam": locatie3.naam},
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

        self.assertEqual(len(create_data["locaties"]), 3)

        self.assertEqual(create_data["locaties"][0]["uuid"], str(locatie1.uuid))
        self.assertEqual(create_data["locaties"][0]["naam"], locatie1.naam)

        self.assertEqual(create_data["locaties"][1]["uuid"], str(locatie2.uuid))
        self.assertEqual(create_data["locaties"][1]["naam"], locatie2.naam)

        self.assertEqual(create_data["locaties"][2]["uuid"], str(locatie3.uuid))
        self.assertEqual(create_data["locaties"][2]["naam"], locatie3.naam)

        with self.subTest("test_update_product_with_locaties_naam"):
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
                    "owmsLabel": "organisatie",
                    "owmsIdentifier": "https://www.organisatie.com",
                },
                "bevoegdeOrganisatie": None,
                "locaties": [
                    {"naam": locatie1.naam},
                    {"naam": locatie2.naam},
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

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(len(update_data["locaties"]), 2)

            self.assertEqual(update_data["locaties"][0]["uuid"], str(locatie1.uuid))
            self.assertEqual(update_data["locaties"][0]["naam"], locatie1.naam)

            self.assertEqual(update_data["locaties"][1]["uuid"], str(locatie2.uuid))
            self.assertEqual(update_data["locaties"][1]["naam"], locatie2.naam)

    def test_create_product_with_gerelateerde_producten_upn_label(self):
        third_upn = UniformeProductnaamFactory.create(
            upn_label="third",
            upn_uri="https://www.third.com",
        )
        third_generiek_product = GeneriekProductFactory.create(
            upn=third_upn,
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

        product2 = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=self.catalogus,
            bevoegde_organisatie=self.bevoegde_organisatie,
            product_aanwezig=True,
        )
        product_versie2 = ProductVersieFactory.create(
            product=product2, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie2)

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

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsLabel": "referentie",
                "owmsIdentifier": "https://www.referentie.com",
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
                {"upnLabel": product2.generiek_product.upn.upn_label},
                {"upnLabel": product3.generiek_product.upn.upn_label},
            ],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["gerelateerdeProducten"]), 2)

        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnLabel"],
            product2.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            product2.generiek_product.upn.upn_uri,
        )

        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnLabel"],
            product3.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnUri"],
            product3.generiek_product.upn.upn_uri,
        )

        with self.subTest("test_update_product_with_gerelateerde_producten_upn_label"):
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
                    "owmsLabel": "referentie",
                    "owmsIdentifier": "https://www.referentie.com",
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
                    {"upnLabel": product3.generiek_product.upn.upn_label},
                ],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(len(update_data["gerelateerdeProducten"]), 1)

            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnLabel"],
                product3.generiek_product.upn.upn_label,
            )
            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnUri"],
                product3.generiek_product.upn.upn_uri,
            )

    def test_create_product_with_gerelateerde_producten_upn_uri(self):
        third_upn = UniformeProductnaamFactory.create(
            upn_label="third",
            upn_uri="https://www.third.com",
        )
        third_generiek_product = GeneriekProductFactory.create(
            upn=third_upn,
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

        product2 = SpecifiekProductFactory.create(
            generiek_product=self.second_generiek_product,
            referentie_product=self.second_referentie_product,
            catalogus=self.catalogus,
            bevoegde_organisatie=self.bevoegde_organisatie,
            product_aanwezig=True,
        )
        product_versie2 = ProductVersieFactory.create(
            product=product2, publicatie_datum=None
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_versie2)

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

        body = {
            "upnLabel": self.generiek_product.upn.upn_label,
            "upnUri": self.generiek_product.upn.upn_uri,
            "publicatieDatum": None,
            "productAanwezig": 1,
            "productValtOnder": None,
            "verantwoordelijkeOrganisatie": {
                "owmsLabel": "referentie",
                "owmsIdentifier": "https://www.referentie.com",
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
                {"upnUri": product2.generiek_product.upn.upn_uri},
                {"upnUri": product3.generiek_product.upn.upn_uri},
            ],
        }

        create_response = self.client.post(
            list_url,
            data=json.dumps(body),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        create_data = create_response.json()

        self.assertEqual(len(create_data["gerelateerdeProducten"]), 2)

        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnLabel"],
            product2.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][0]["upnUri"],
            product2.generiek_product.upn.upn_uri,
        )

        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnLabel"],
            product3.generiek_product.upn.upn_label,
        )
        self.assertEqual(
            create_data["gerelateerdeProducten"][1]["upnUri"],
            product3.generiek_product.upn.upn_uri,
        )

        with self.subTest("test_update_product_with_gerelateerde_producten_upn_uri"):
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
                    "owmsLabel": "referentie",
                    "owmsIdentifier": "https://www.referentie.com",
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
                    {"upnUri": product3.generiek_product.upn.upn_uri},
                ],
            }

            update_response = self.client.put(
                detail_url,
                data=json.dumps(body),
                content_type="application/json",
            )

            self.assertEqual(update_response.status_code, status.HTTP_200_OK)

            update_data = update_response.json()

            self.assertEqual(len(update_data["gerelateerdeProducten"]), 1)

            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnLabel"],
                product3.generiek_product.upn.upn_label,
            )
            self.assertEqual(
                update_data["gerelateerdeProducten"][0]["upnUri"],
                product3.generiek_product.upn.upn_uri,
            )

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

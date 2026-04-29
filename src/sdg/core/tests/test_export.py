import io

from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.translation import gettext as _

import pandas as pd
from freezegun import freeze_time

from sdg.accounts.tests.factories import (
    RoleFactory,
    SuperUserFactory,
    UserFactory,
    UserInvitationFactory,
)
from sdg.organisaties.tests.factories.overheid import (
    BevoegdeOrganisatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedProductFactory,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ProductFactory,
    ProductVersieFactory,
    SpecifiekProductFactory,
    SpecifiekProductVersieFactory,
)

from ..constants import (
    AccountStatus,
    DoelgroepChoices,
    GenericProductStatus,
    Rol,
    Systeemrechten,
)
from ..export import ApplicationExporter
from .factories.catalogus import ProductenCatalogusFactory
from .factories.logius import OverheidsorganisatieFactory


class ApplicationExportTest(TestCase):
    def test_empty_export(self):
        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)

            file = pd.ExcelFile(export_file)
            for sheet_name in file.sheet_names:
                with self.subTest(sheet_name=sheet_name):
                    dataframe = file.parse(sheet_name)
                    self.assertTrue(dataframe.empty)

    def test_accounts_info(self):
        lokale_overheid_1 = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht"
        )
        lokale_overheid_2 = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="Nimma"
        )

        inviter = UserFactory.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@email.net",
        )
        with freeze_time("2020-01-01T00:00:00Z"):
            user = SuperUserFactory.create(
                first_name="Jane",
                last_name="Doe",
                email="jane.doe@email.net",
                last_login=timezone.now(),
            )
            UserInvitationFactory.create(
                user=user,
                inviter=inviter,
                accepted=True,
            )

        RoleFactory.create(
            user=user,
            lokale_overheid=lokale_overheid_1,
            is_beheerder=True,
            is_redacteur=False,
            is_raadpleger=False,
        )

        RoleFactory.create(
            user=user,
            lokale_overheid=lokale_overheid_2,
            is_beheerder=False,
            is_redacteur=True,
            is_raadpleger=True,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            file = pd.ExcelFile(export_file)
            dataframe = file.parse("Accounts info")

        with self.subTest("first row"):
            row = dataframe.iloc[0].to_dict()
            self.assertEqual(
                row,
                {
                    "Unnamed: 0": 0,
                    "id": user.pk,
                    "gemeente_id": lokale_overheid_1.pk,
                    "organisatie": "UUUUtrecht",
                    "gemeente": "UUUUtrecht",
                    "voornaam": "Jane",
                    "achternaam": "Doe",
                    "naam": "Jane Doe",
                    "email": "jane.doe@email.net",
                    "uitgenodigd door": "John Doe",
                    "date_joined": "1 January, 2020, 00:00",
                    "last_login": "1 January, 2020, 00:00",
                    "account status": _("heeft ingelogd"),
                    "accepted": True,
                    "created": "1 January, 2020, 00:00",
                    "is_active": True,
                    "rol": _("beheerder"),
                    "is_beheerder": True,
                    "is_redacteur": False,
                    "is_raadpleger": False,
                    "systeemrechten": _("superuser"),
                    "is_superuser": True,
                    "is_staff": True,
                },
            )

        with self.subTest("second row"):
            row = dataframe.iloc[1].to_dict()
            self.assertEqual(
                row,
                {
                    "Unnamed: 0": 1,
                    "id": user.pk,
                    "gemeente_id": lokale_overheid_2.pk,
                    "organisatie": "Nimma",
                    "gemeente": "Nimma",
                    "voornaam": "Jane",
                    "achternaam": "Doe",
                    "naam": "Jane Doe",
                    "email": "jane.doe@email.net",
                    "uitgenodigd door": "John Doe",
                    "date_joined": "1 January, 2020, 00:00",
                    "last_login": "1 January, 2020, 00:00",
                    "account status": _("heeft ingelogd"),
                    "accepted": 1,
                    "created": "1 January, 2020, 00:00",
                    "is_active": 1,
                    "rol": _("redacteur"),
                    "is_beheerder": 0,
                    "is_redacteur": 1,
                    "is_raadpleger": 1,
                    "systeemrechten": _("superuser"),
                    "is_superuser": 1,
                    "is_staff": 1,
                },
            )

    def test_accounts_info_combined_fields(self):
        lokale_overheid_1 = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht"
        )

        with freeze_time("2020-01-01T00:00:00Z"):
            user_1 = SuperUserFactory.create(
                first_name="Jane",
                last_name="Doe",
                email="jane.doe@email.net",
            )
            UserInvitationFactory.create(
                user=user_1,
                accepted=True,
                created=timezone.now(),
            )
            RoleFactory.create(
                user=user_1,
                lokale_overheid=lokale_overheid_1,
                is_beheerder=True,
                is_redacteur=True,
                is_raadpleger=True,
            )

            user_2 = UserFactory.create(
                first_name="John",
                last_name="Doe",
                email="john.doe@email.net",
                last_login=timezone.now(),
                is_staff=True,
            )
            RoleFactory.create(
                user=user_2,
                lokale_overheid=lokale_overheid_1,
                is_beheerder=False,
                is_redacteur=True,
                is_raadpleger=True,
            )

            user_3 = UserFactory.create(
                first_name="J",
                last_name="Doe",
                email="j.doe@email.net",
            )
            RoleFactory.create(
                user=user_3,
                lokale_overheid=lokale_overheid_1,
                is_beheerder=False,
                is_redacteur=False,
                is_raadpleger=True,
            )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Accounts info",
            )

        with self.subTest("first user"):
            row = df.iloc[0]
            self.assertEqual(row["naam"], "Jane Doe")
            # user hasn't logged in but has been invited.
            self.assertEqual(row["account status"], AccountStatus.created.label)
            self.assertEqual(row["rol"], Rol.is_beheerder.label)
            # user is super user.
            self.assertEqual(row["systeemrechten"], Systeemrechten.is_superuser.label)

        with self.subTest("second user"):
            row = df.iloc[1]
            self.assertEqual(row["naam"], "John Doe")
            # user has logged in.
            self.assertEqual(row["account status"], AccountStatus.logged_in.label)
            self.assertEqual(row["rol"], Rol.is_redacteur.label)
            # user is staff but not superuser
            self.assertEqual(row["systeemrechten"], Systeemrechten.is_staff.label)

        with self.subTest("third user"):
            row = df.iloc[2]
            self.assertEqual(row["naam"], "J Doe")
            # User hasn't logged in and hasn't been invited
            self.assertEqual(row["account status"], AccountStatus.empty.label)
            self.assertEqual(row["rol"], Rol.is_raadpleger.label)
            # user isn't staff or superuser
            self.assertEqual(row["systeemrechten"], Systeemrechten.empty.label)

    def test_referentie_municipality_data(self):
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid__organisatie__owms_pref_label="UUUUtrecht",
            is_referentie_catalogus=True,
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=catalogus.lokale_overheid
        )

        for status in GenericProductStatus.values.keys():
            generiek_product = GeneriekProductFactory.create(product_status=status)
            product = SpecifiekProductFactory.create(
                generiek_product=generiek_product,
                catalogus=catalogus,
                bevoegde_organisatie=bevoegde_organisatie,
            )
            SpecifiekProductVersieFactory.create(
                product=product, publicatie_datum=timezone.now(), versie=1
            )

        SpecifiekProductVersieFactory.create(
            product__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            product__catalogus=catalogus,
            publicatie_datum=None,
            product__bevoegde_organisatie=bevoegde_organisatie,
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.ExcelFile(export_file)
            document_info = df.parse("Document info")
            row = document_info.iloc[0].to_dict()

        # these are the statuses which should be included in the queryset.
        # and in this case published
        self.assertEqual(
            GenericProductStatus.get_cms_included(reference=True).sort(),
            [
                GenericProductStatus.READY_FOR_PUBLICATION,
                GenericProductStatus.READY_FOR_ADMIN,
                GenericProductStatus.EXPIRED,
                GenericProductStatus.NEW,
                GenericProductStatus.EOL,
            ].sort(),
        )

        self.assertEqual(
            row,
            {
                "Unnamed: 0": 0,
                "gemeente": "UUUUtrecht",
                "aantal gepubliceerde teksten": 5,
                "aantal conceptteksten": 1,
                "aantal teksten": 6,
            },
        )

    def test_municipality_data(self):
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid__organisatie__owms_pref_label="UUUUtrecht"
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=catalogus.lokale_overheid
        )

        for status in GenericProductStatus.values.keys():
            generiek_product = GeneriekProductFactory.create(product_status=status)
            product = SpecifiekProductFactory.create(
                generiek_product=generiek_product,
                catalogus=catalogus,
                bevoegde_organisatie=bevoegde_organisatie,
            )
            SpecifiekProductVersieFactory.create(
                product=product, publicatie_datum=timezone.now(), versie=1
            )

        SpecifiekProductVersieFactory.create(
            product__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            product__catalogus=catalogus,
            publicatie_datum=None,
            product__bevoegde_organisatie=bevoegde_organisatie,
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.ExcelFile(export_file)
            document_info = df.parse("Document info")
            row = document_info.iloc[0].to_dict()

        # these are the statuses which should be included in the queryset.
        # and in this case published
        self.assertEqual(
            GenericProductStatus.get_cms_included().sort(),
            [
                GenericProductStatus.READY_FOR_PUBLICATION,
                GenericProductStatus.EXPIRED,
                GenericProductStatus.EOL,
            ].sort(),
        )

        self.assertEqual(
            row,
            {
                "Unnamed: 0": 0,
                "gemeente": "UUUUtrecht",
                "aantal gepubliceerde teksten": 3,
                "aantal conceptteksten": 1,
                "aantal teksten": 4,
            },
        )

    @freeze_time("2026-01-01")
    def test_municipality_info_org_no_longer_exists(self):
        catalogus = ProductenCatalogusFactory.create(
            lokale_overheid__organisatie__owms_pref_label="UUUUtrecht",
            lokale_overheid__organisatie__owms_end_date=timezone.now(),
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=catalogus.lokale_overheid
        )
        product = ProductFactory.create(
            catalogus=catalogus,
            bevoegde_organisatie=bevoegde_organisatie,
            generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
        )
        SpecifiekProductVersieFactory.create(
            product=product,
            publicatie_datum=timezone.now(),
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Document info",
            )

        self.assertTrue(df.empty)

    @freeze_time("2020-01-01T00:00:00Z")
    def test_product_default_data(self):
        overheids_org = OverheidsorganisatieFactory.create(owms_pref_label="org")
        lokale_overheid = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht"
        )
        catalogus = ProductenCatalogusFactory.create(lokale_overheid=lokale_overheid)
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
            organisatie__owms_pref_label="UUUUtrecht (2)",
        )
        generiek_product = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            verantwoordelijke_organisaties=[overheids_org.pk],
            upn__upn_label="product name",
            upn__thema__informatiegebied__informatiegebied="informatiegebied",
            doelgroep="",
        )

        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="nl",
            product_titel="product naam",
            generieke_tekst="tekst",
            korte_omschrijving="een korte beschrijving",
            laatst_gewijzigd=timezone.now(),
            datum_check=timezone.now(),
            verwijzing_links=[["link", "https://www.link.com", "een publieke link"]],
            landelijke_link="https://www.link.com/nl",
        )
        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="en",
            product_titel="product name",
            generieke_tekst="text",
            korte_omschrijving="a short description",
            laatst_gewijzigd=timezone.now(),
            datum_check=timezone.now(),
            verwijzing_links=[["link", "https://www.link.com", "a public link"]],
            landelijke_link="https://www.link.com/en",
        )

        product = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            catalogus=catalogus,
            product_aanwezig=False,
            bevoegde_organisatie=bevoegde_organisatie,
            heeft_kosten=True,
        )
        version = ProductVersieFactory.create(
            product=product,
            publicatie_datum=timezone.now(),
            versie=1,
        )
        LocalizedProductFactory.create(
            product_versie=version,
            taal="nl",
            product_titel_decentraal="decentrale titel",
            specifieke_tekst="wat tekst",
            verwijzing_links=[["bla", "https://www.bla.nl"]],
            procedure_beschrijving="omschrijving over het product",
            vereisten="niks",
            bewijs="de documentatie",
            bezwaar_en_beroep="bezwaar en beroep",
            kosten_en_betaalmethoden="kosten",
            uiterste_termijn="gisteren",
            wtd_bij_geen_reactie="huilen",
            decentrale_procedure_label="decentrale label",
            decentrale_procedure_link="https://www.procedure_link.nl",
            product_valt_onder_toelichting="het valt hier onder omdat dit zo is.",
            product_aanwezig_toelichting="het is aanwezig omdat het aanwezig is.",
        )
        LocalizedProductFactory.create(
            product_versie=version,
            taal="en",
            product_titel_decentraal="decentrale titel",
            specifieke_tekst="some text",
            verwijzing_links=[["bla", "https://www.bla.com"]],
            procedure_beschrijving="description about the product",
            vereisten="nothing",
            bewijs="the documentatie",
            bezwaar_en_beroep="objection and appeal",
            kosten_en_betaalmethoden="costs",
            uiterste_termijn="yesterday",
            wtd_bij_geen_reactie="cry",
            decentrale_procedure_label="decentralized label",
            decentrale_procedure_link="https://www.procedure_link.com",
            product_valt_onder_toelichting="It falls under this because that is the case.",
            product_aanwezig_toelichting="It is present because it is present.",
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Product info",
            )
            row = df.iloc[0].to_dict()

        self.assertEqual(
            row,
            {
                "Unnamed: 0": 0,
                "id": product.pk,
                "gemeente": "UUUUtrecht",
                "doelgroep": "",
                "UPN label": "product name",
                "status": "published",
                "aanwezig": False,
                "heeft kosten": True,
                "aanwezig toelichting": "het is aanwezig omdat het aanwezig is.",
                "aanwezig toelichting (en)": "It is present because it is present.",
                "valt onder doelgroep": "",
                "valt onder": "",
                "valt onder toelichting": "het valt hier onder omdat dit zo is.",
                "valt onder toelichting (en)": "It falls under this because that is the case.",
                "valt onder(ja / nee)": "Nee",
                "informatiegebied": "informatiegebied",
                "SDG product": "product name",
                "generieke titel": "product naam",
                "generieke titel (en)": "product name",
                "generieke tekst": "tekst",
                "generieke tekst (en)": "text",
                "specifieke titel": "decentrale titel",
                "specifieke titel (en)": "decentrale titel",
                "specifieke tekst": "wat tekst",
                "specifieke tekst (en)": "some text",
                "procedure beschrijving": "omschrijving over het product",
                "procedure beschrijving (en)": "description about the product",
                "vereisten": "niks",
                "vereisten (en)": "nothing",
                "bewijs": "de documentatie",
                "bewijs (en)": "the documentatie",
                "bezwaar en beroep": "bezwaar en beroep",
                "bezwaar en beroep (en)": "objection and appeal",
                "kosten en betaalmethoden": "kosten",
                "kosten en betaalmethoden (en)": "costs",
                "uiterste termijn": "gisteren",
                "uiterste termijn (en)": "yesterday",
                "wat te doen bij geen reactie": "huilen",
                "wat te doen bij geen reactie (en)": "cry",
                "generieke verwijzing links": "[['link', 'https://www.link.com', 'een publieke link']]",
                "generieke verwijzing links (en)": "[['link', 'https://www.link.com', 'a public link']]",
                "specifieke verwijzing links": "[['bla', 'https://www.bla.nl']]",
                "specifieke verwijzing links (en)": "[['bla', 'https://www.bla.com']]",
                "URL portaal": "",
                "URL portaal (en)": "",
                "decentrale procedure label": "decentrale label",
                "decentrale procedure label (en)": "decentralized label",
                "decentrale procedure link": "https://www.procedure_link.nl",
                "decentrale procedure link (en)": "https://www.procedure_link.com",
                "landelijk verantwoordelijke organisatie": "org",
                "generieke datum check": "1 January, 2020, 00:00",
                "generieke datum check (en)": "1 January, 2020, 00:00",
                "gemaakt op": "1 January, 2020, 00:00",
                "publicatiedatum": "1 January, 2020",
                "laatste wijziging": "1 January, 2020, 00:00",
                "versie": 1,
                "bevoegde organisatie": "UUUUtrecht (2)",
            },
        )

    @override_settings(
        SDG_DOP_URL_TEMPLATE_NL="{product_url}dop_nl/{organisation}/",
        SDG_DOP_URL_TEMPLATE_EN="{product_url}dop_en/{organisation}/",
        SDG_DPC_URL_TEMPLATE_NL="{product_url}dpc_nl/{organisation}/",
        SDG_DPC_URL_TEMPLATE_EN="{product_url}dpc_en/{organisation}/",
    )
    def test_product_url_portaal(self):
        lokale_overheid = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht"
        )
        catalogus = ProductenCatalogusFactory.create(lokale_overheid=lokale_overheid)
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
        )

        generiek_product = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            doelgroep=DoelgroepChoices.burger,
        )
        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="nl",
            landelijke_link="https://www.link.com/",
        )
        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="en",
            landelijke_link="https://www.link.com/",
        )
        product_1 = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            catalogus=catalogus,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        ProductVersieFactory.create(
            product=product_1,
            publicatie_datum=timezone.now(),
            versie=1,
        )

        generiek_product = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            doelgroep=DoelgroepChoices.bedrijf,
        )
        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="nl",
            landelijke_link="https://www.link.com/",
        )
        LocalizedGeneriekProductFactory.create(
            generiek_product=generiek_product,
            taal="en",
            landelijke_link="https://www.link.com/",
        )
        product_2 = SpecifiekProductFactory.create(
            generiek_product=generiek_product,
            catalogus=catalogus,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        ProductVersieFactory.create(
            product=product_2,
            publicatie_datum=timezone.now(),
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Product info",
            )

        with self.subTest("burger"):
            row = df.iloc[0]
            self.assertEqual(
                row["URL portaal"], "https://www.link.com/dpc_nl/uuuutrecht/"
            )
            self.assertEqual(
                row["URL portaal (en)"], "https://www.link.com/dpc_en/uuuutrecht/"
            )

        with self.subTest("bedrijf"):
            row = df.iloc[1]
            self.assertEqual(
                row["URL portaal"], "https://www.link.com/dop_nl/uuuutrecht/"
            )
            self.assertEqual(
                row["URL portaal (en)"], "https://www.link.com/dop_en/uuuutrecht/"
            )

    def test_product_show_products(self):
        lokale_overheid = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht"
        )
        catalogus = ProductenCatalogusFactory.create(lokale_overheid=lokale_overheid)
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
        )
        product_scheduled, product_concept, latest_version, concept, scheduled = (
            ProductFactory.create_batch(
                5, catalogus=catalogus, bevoegde_organisatie=bevoegde_organisatie
            )
        )

        # published + scheduled
        ProductVersieFactory.create(
            product=product_scheduled,
            publicatie_datum=timezone.now(),
            versie=1,
        )
        ProductVersieFactory.create(
            product=product_scheduled,
            publicatie_datum=timezone.now() + timezone.timedelta(days=1),
            versie=2,
        )

        # published + concept
        ProductVersieFactory.create(
            product=product_concept,
            publicatie_datum=timezone.now(),
            versie=1,
        )
        ProductVersieFactory.create(
            product=product_concept,
            publicatie_datum=None,
            versie=2,
        )

        # 3 published
        ProductVersieFactory.create(
            product=latest_version,
            publicatie_datum=timezone.now(),
            versie=1,
        )
        ProductVersieFactory.create(
            product=latest_version,
            publicatie_datum=timezone.now(),
            versie=2,
        )
        ProductVersieFactory.create(
            product=latest_version,
            publicatie_datum=timezone.now(),
            versie=3,
        )

        # concept
        ProductVersieFactory.create(product=concept, publicatie_datum=None, versie=1)

        # scheduled
        ProductVersieFactory.create(
            product=scheduled,
            publicatie_datum=timezone.now() + timezone.timedelta(days=1),
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Product info",
            )

        with self.subTest("don't show scheduled versions over published versions"):
            row = df.iloc[0]
            self.assertEqual(row["id"], product_scheduled.id)
            self.assertEqual(row["versie"], 1)

        with self.subTest("don't show concept versions over published versions"):
            row = df.iloc[1]
            self.assertEqual(row["id"], product_concept.id)
            self.assertEqual(row["versie"], 1)

        with self.subTest("published latest version"):
            # always show latest version
            row = df.iloc[2]
            self.assertEqual(row["id"], latest_version.id)
            self.assertEqual(row["versie"], 3)

        with self.subTest("show concept when no published versions"):
            row = df.iloc[3]
            self.assertEqual(row["id"], concept.id)
            self.assertEqual(row["versie"], 1)

        with self.subTest("show scheduled when no published versions"):
            row = df.iloc[4]
            self.assertEqual(row["id"], scheduled.id)
            self.assertEqual(row["versie"], 1)

    @freeze_time("2026-01-01")
    def test_product_org_no_longer_exists(self):
        lokale_overheid = LokaleOverheidFactory.create(
            organisatie__owms_pref_label="UUUUtrecht",
            organisatie__owms_end_date=timezone.now() - timezone.timedelta(days=1),
        )
        catalogus = ProductenCatalogusFactory.create(lokale_overheid=lokale_overheid)
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            lokale_overheid=lokale_overheid,
        )
        product = ProductFactory.create(
            catalogus=catalogus, bevoegde_organisatie=bevoegde_organisatie
        )
        ProductVersieFactory.create(
            product=product,
            publicatie_datum=timezone.now(),
            versie=1,
        )

        with io.BytesIO() as export_file:
            ApplicationExporter(export_file)
            df = pd.read_excel(
                export_file,
                keep_default_na=False,
                na_values=[],
                sheet_name="Product info",
            )

        self.assertTrue(df.empty)

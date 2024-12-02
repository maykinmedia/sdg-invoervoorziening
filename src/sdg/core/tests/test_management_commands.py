import os
from datetime import date, datetime
from io import StringIO
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from dateutil.relativedelta import relativedelta

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.constants import DoelgroepChoices
from sdg.core.management.utils import update_generic_products
from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.config import SiteConfigurationFactory
from sdg.core.tests.factories.logius import ThemaFactory, UniformeProductnaamFactory
from sdg.organisaties.models import LokaleOverheid
from sdg.organisaties.tests.factories.overheid import BevoegdeOrganisatieFactory
from sdg.producten.management.commands.check_broken_links import (
    Command as CheckBrokenLinksCommand,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ReferentieProductFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductVersieFactory,
)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class CommandTestCase(TestCase):
    def call_command(self, command_name, *args, **kwargs):
        out = StringIO()
        call_command(
            command_name,
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()


class TestImportData(CommandTestCase):
    def test_load_government_orgs(self):
        out = self.call_command(
            "load_government_orgs",
            os.path.join(TESTS_DIR, "data/Overheidsorganisatie.xml"),
        )

        self.assertIn("Done", out)
        self.assertIn("(8 objects)", out)
        self.assertEqual(8, Overheidsorganisatie.objects.count())
        self.assertEqual(0, LokaleOverheid.objects.count())

        organisatie = Overheidsorganisatie.objects.first()
        self.assertEqual(organisatie.owms_pref_label, "'s-Graveland")
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/'s-Graveland_(gemeente)",
            organisatie.owms_identifier,
        )
        self.assertEqual(datetime(2001, 12, 31), organisatie.owms_end_date)

    def test_load_municipalities_before_gov_orgs(self):
        out = self.call_command(
            "load_organisation_subset", os.path.join(TESTS_DIR, "data/Gemeente.xml")
        )

        self.assertIn("Done", out)
        self.assertIn("(0 objects)", out)
        self.assertEqual(0, Overheidsorganisatie.objects.count())

    def test_load_municipalities_after_gov_orgs(self):
        self.call_command(
            "load_government_orgs",
            os.path.join(TESTS_DIR, "data/Overheidsorganisatie.xml"),
        )

        out = self.call_command(
            "load_organisation_subset", os.path.join(TESTS_DIR, "data/Gemeente.xml")
        )

        self.assertIn("Done", out)
        self.assertIn("(5 objects)", out)
        self.assertEqual(5, LokaleOverheid.objects.count())

        lokale_overheid = LokaleOverheid.objects.first()
        self.assertEqual(lokale_overheid.organisatie.owms_pref_label, "'s-Graveland")
        self.assertEqual(lokale_overheid.bevoegde_organisaties.count(), 1)
        self.assertEqual(
            lokale_overheid.bevoegde_organisaties.get().organisatie,
            lokale_overheid.organisatie,
        )

    def test_load_informatiegebieden(self):
        out = self.call_command(
            "load_informatiegebieden",
            os.path.join(TESTS_DIR, "data/SDG-Informatiegebieden.csv"),
        )

        self.assertIn("Done", out)
        self.assertIn("(24 objects)", out)
        self.assertEqual(4, Informatiegebied.objects.count())
        self.assertEqual(24, Thema.objects.count())

        informatiegebied = Informatiegebied.objects.get(
            informatiegebied="Reizen binnen de Unie"
        )
        self.assertEqual(informatiegebied.informatiegebied, "Reizen binnen de Unie")
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/sdg_reizUnie",
            informatiegebied.informatiegebied_uri,
        )

    def test_load_upn(self):
        thema_1 = ThemaFactory.create(
            code="A1",
            informatiegebied__informatiegebied_uri="http://standaarden.overheid.nl/owms/terms/sdg_reizUnie",
        )
        ThemaFactory.create(
            code="L2",
            informatiegebied__informatiegebied_uri="http://standaarden.overheid.nl/owms/terms/sdg_belastingen",
        )
        out = self.call_command(
            "load_upn", os.path.join(TESTS_DIR, "data/UPL-actueel.csv")
        )

        self.assertIn("Done", out)
        self.assertIn("(16 objects)", out)
        self.assertEqual(UniformeProductnaam.objects.count(), 16)

        upn = UniformeProductnaam.objects.first()
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
            upn.upn_uri,
        )
        self.assertEqual("aanleunwoning", upn.upn_label)
        self.assertEqual(False, upn.rijk)
        self.assertEqual(True, upn.burger)

        # ensure themes are correct
        upn = UniformeProductnaam.objects.get(upn_label="adoptie")
        self.assertEqual(thema_1, upn.thema)
        self.assertEqual("A1", upn.thema.code)

        # ensure target groups are correct
        self.assertFalse(upn.is_verwijderd)
        self.assertListEqual(upn.sdg, ["A1", "L2"])

        with self.subTest("test_load_upn_is_verwijderd"):
            self.call_command(
                "load_upn",
                os.path.join(TESTS_DIR, "data/UPL-actueel-without-adoptie.csv"),
            )
            upn = UniformeProductnaam.objects.get(upn_label="adoptie")

            self.assertTrue(upn.is_verwijderd)

            with self.subTest("test_load_upn_undo_is_verwijderd"):
                self.call_command(
                    "load_upn",
                    os.path.join(TESTS_DIR, "data/UPL-actueel.csv"),
                )
                upn = UniformeProductnaam.objects.get(upn_label="adoptie")

                self.assertFalse(upn.is_verwijderd)


class TestUpdateGenericProductsTests(CommandTestCase):
    def setUp(self):
        self.upn_1 = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=True,
            sdg=["L2"],  # eu-bedrijf only
        )
        self.upn_2 = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=True,
            sdg=["A1", "L2"],  # eu-burger and eu-bedrijf
        )
        self.upn_3 = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=True,
            sdg=[],  # Not an SDG product
        )

    def test_create_generic_products_1_target_group(self):
        self.assertEqual(self.upn_1.generieke_producten.count(), 0)

        update_generic_products(self.upn_1)

        self.assertEqual(self.upn_1.generieke_producten.count(), 1)
        gp = self.upn_1.generieke_producten.first()
        self.assertEqual(gp.doelgroep, DoelgroepChoices.bedrijf)
        self.assertEqual(gp.vertalingen.count(), 2)

    def test_create_generic_products_2_target_groups(self):
        self.assertEqual(self.upn_2.generieke_producten.count(), 0)

        update_generic_products(self.upn_2)

        self.assertEqual(self.upn_2.generieke_producten.count(), 2)

        gp_bedrijf = self.upn_2.generieke_producten.get(
            doelgroep=DoelgroepChoices.bedrijf
        )
        gp_burger = self.upn_2.generieke_producten.get(
            doelgroep=DoelgroepChoices.burger
        )

        self.assertEqual(gp_bedrijf.vertalingen.count(), 2)
        self.assertEqual(gp_burger.vertalingen.count(), 2)

    def test_delete_old_generic_product_no_sdg_codes(self):
        # This UPN has a Generiek Product linked but is no longer an SDG
        # product.
        GeneriekProductFactory.create(upn=self.upn_3)

        self.assertEqual(self.upn_3.generieke_producten.count(), 1)

        update_generic_products(self.upn_3)

        self.assertEqual(self.upn_3.generieke_producten.count(), 0)

    def test_delete_old_generic_product_with_incorrect_sdg_codes(self):
        # This UPN has a Generiek Product linked that has no target group and
        # an invalid (no SDG code in the UPN) target group. Both should be
        # deleted, leaving only 1.
        GeneriekProductFactory.create(
            upn=self.upn_1, doelgroep=DoelgroepChoices.bedrijf
        )
        GeneriekProductFactory.create(upn=self.upn_1, doelgroep=DoelgroepChoices.burger)
        GeneriekProductFactory.create(upn=self.upn_1, doelgroep="")

        self.assertEqual(self.upn_1.generieke_producten.count(), 3)

        update_generic_products(self.upn_1)

        self.assertEqual(self.upn_1.generieke_producten.count(), 1)
        gp = self.upn_1.generieke_producten.first()
        self.assertEqual(gp.doelgroep, DoelgroepChoices.bedrijf)

    def test_delete_old_generic_product_with_concept_products(self):
        # This UPN has a Generiek Product linked but is no longer an SDG
        # product. However, a concept product versionwas already created.
        SpecifiekProductVersieFactory.create(
            product__referentie_product__generiek_product__upn=self.upn_3
        )

        self.assertEqual(self.upn_3.generieke_producten.count(), 1)

        update_generic_products(self.upn_3)

        self.assertEqual(self.upn_3.generieke_producten.count(), 0)

    def test_eol_generic_products_that_cannot_be_removed(self):
        # This UPN has a Generiek Product linked but is no longer an SDG
        # product. However, a published product versionwas already created.
        SpecifiekProductVersieFactory.create(
            product__referentie_product__generiek_product__upn=self.upn_3,
            publicatie_datum=datetime.today(),
        )

        self.assertEqual(self.upn_3.generieke_producten.count(), 1)

        update_generic_products(self.upn_3)

        self.assertEqual(self.upn_3.generieke_producten.count(), 1)
        gp = self.upn_3.generieke_producten.first()
        self.assertAlmostEqual(gp.eind_datum, date.today())


class TestAutofill(CommandTestCase):
    def setUp(self):
        # The basis for autofill is the existance of generic products and
        # matching catalogs, to create reference products.

        self.reference_catalog = ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["sdg", "waterschap"],
            is_referentie_catalogus=True,
        )

        # A catalog that uses another filter
        self.reference_catalog_other_filter = ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["sdg", "gemeente"],
            is_referentie_catalogus=True,
        )

        # A catalog that should not be filled
        self.reference_catalog_no_autofill = ProductenCatalogusFactory.create(
            autofill=False,
            autofill_upn_filter=["sdg", "waterschap"],
            is_referentie_catalogus=True,
        )

        # A specific catalog
        self.specific_catalog = ProductenCatalogusFactory.create(
            autofill=True,  # This is typically False
            autofill_upn_filter=["sdg", "waterschap"],  # This is typically empty
            is_referentie_catalogus=False,
        )

        self.gp_1_bedrijf = GeneriekProductFactory.create(
            upn__provincie=True,
            upn__waterschap=True,
            upn__sdg=["L2"],
            doelgroep="eu-bedrijf",
        )
        self.gp_2_bedrijf = GeneriekProductFactory.create(
            upn__provincie=True,
            upn__waterschap=True,
            upn__sdg=["A1", "L2"],
            doelgroep="eu-bedrijf",
        )
        self.gp_2_burger = GeneriekProductFactory.create(
            upn=self.gp_2_bedrijf.upn,
            doelgroep="eu-burger",
        )

    def test_autofill_catalogs(self):

        self.assertEqual(self.reference_catalog.producten.count(), 0)
        self.assertEqual(self.reference_catalog_other_filter.producten.count(), 0)
        self.assertEqual(self.reference_catalog_no_autofill.producten.count(), 0)
        self.assertEqual(self.specific_catalog.producten.count(), 0)

        out = self.call_command("autofill")

        self.assertIn("Created new product", out)

        with self.subTest("test_autofill_matching_with_generic"):

            self.assertEqual(self.reference_catalog.producten.count(), 3)
            self.assertEqual(self.specific_catalog.producten.count(), 0)

            for reference_product in self.reference_catalog.producten.all():
                self.assertEqual(reference_product.versies.count(), 1)
                reference_version = reference_product.versies.get()
                self.assertEqual(reference_version.vertalingen.count(), 2)

        with self.subTest("test_autofill_not_matching_with_generic"):

            self.assertEqual(self.reference_catalog_other_filter.producten.count(), 0)

        with self.subTest("test_autofill_with_no_autofill_catalogs"):

            self.assertEqual(self.reference_catalog_no_autofill.producten.count(), 0)

        with self.subTest("test_autofill_not_enabled"):

            self.assertEqual(self.specific_catalog.producten.count(), 0)

    def test_correct_missing_initial_version(self):
        reference_product = ReferentieProductFactory.create(
            generiek_product=self.gp_1_bedrijf, catalogus=self.reference_catalog
        )

        self.assertEqual(reference_product.versies.count(), 0)

        out = self.call_command("autofill")

        self.assertIn("Created new product", out)

        self.assertEqual(self.reference_catalog.producten.count(), 3)

        for rp in self.reference_catalog.producten.all():
            self.assertEqual(rp.versies.count(), 1)
            rv = reference_product.versies.get()
            self.assertEqual(rv.vertalingen.count(), 2)

    def test_add_missing_bevoegde_organisatie(self):
        self.reference_catalog.lokale_overheid.bevoegde_organisaties.all().delete()
        self.reference_catalog.refresh_from_db()

        out = self.call_command("autofill")

        self.assertIn("Corrected missing default bevoegde organisatie", out)

        bos = self.reference_catalog.lokale_overheid.bevoegde_organisaties.all()
        self.assertEqual(bos.count(), 1)
        self.assertEqual(
            bos.get().organisatie, self.reference_catalog.lokale_overheid.organisatie
        )

    def test_correct_bevoegde_organisatie(self):
        self.reference_catalog.lokale_overheid.bevoegde_organisaties.all().delete()
        self.reference_catalog.refresh_from_db()

        other_bo = BevoegdeOrganisatieFactory.create(
            lokale_overheid=self.reference_catalog.lokale_overheid
        )
        self.reference_catalog.lokale_overheid.bevoegde_organisaties.add(other_bo)

        out = self.call_command("autofill")

        self.assertIn("Corrected missing default bevoegde organisatie", out)

        bos = self.reference_catalog.lokale_overheid.bevoegde_organisaties.all()
        self.assertEqual(bos.count(), 2)


class TestSendNotificationMail(CommandTestCase):
    def setUp(self):
        self.yesterday = date.today() - relativedelta(days=1)
        self.config = SiteConfigurationFactory.create(
            mail_text_changes_last_sent=self.yesterday
        )
        self.user1, self.user2, self.user3 = UserFactory.create_batch(3)
        RoleFactory.create(user=self.user1, ontvangt_mail=True, is_beheerder=True)
        RoleFactory.create(user=self.user2, ontvangt_mail=True, is_redacteur=True)
        RoleFactory.create(user=self.user3, ontvangt_mail=False, is_raadpleger=True)

        self.ref_product1, self.ref_product2 = ReferentieProductFactory.create_batch(2)
        self._ref_product1_versie1 = ReferentieProductVersieFactory.create(
            product=self.ref_product1, versie=1
        )
        self._ref_product2_versie1 = ReferentieProductVersieFactory.create(
            product=self.ref_product2, versie=1
        )

    def test_send_no_mail_when_no_changes(self):
        out = self.call_command("send_notification_mail")
        self.assertIn(
            f"No changed products found in the past {settings.SDG_MAIL_TEXT_CHANGES_EVERY_DAYS} days.",
            out,
        )
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(self.config.mail_text_changes_last_sent, self.yesterday)

    def test_subscribed_users_get_mail(self):
        ReferentieProductVersieFactory.create(
            product=self.ref_product1,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )
        ReferentieProductVersieFactory.create(
            product=self.ref_product2,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )

        out = self.call_command("send_notification_mail")

        self.config.refresh_from_db()

        self.assertIn("Successfully send emails to 2 user(s)", out)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], self.user1.email)
        self.assertEqual(mail.outbox[1].to[0], self.user2.email)
        self.assertEqual(self.config.mail_text_changes_last_sent, date.today())

    def test_user_flag(self):
        ReferentieProductVersieFactory.create(
            product=self.ref_product1,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )
        ReferentieProductVersieFactory.create(
            product=self.ref_product2,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )

        out = self.call_command("send_notification_mail", "--user", self.user1.email)

        self.config.refresh_from_db()

        self.assertIn("Successfully send emails to 1 user(s)", out)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user1.email)
        self.assertEqual(self.config.mail_text_changes_last_sent, date.today())

    def test_user_flag_with_eligable_user(self):
        ReferentieProductVersieFactory.create(
            product=self.ref_product1,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )
        ReferentieProductVersieFactory.create(
            product=self.ref_product2,
            versie=2,
            gewijzigd_op=date.today(),
            publicatie_datum=date.today(),
        )

        out = self.call_command(
            "send_notification_mail", "--user", f"wrong{self.user1.email}"
        )

        self.config.refresh_from_db()

        self.assertIn("No eligable users found.", out)
        self.assertEqual(len(mail.outbox), 0)


class TestCommandCheckBrokenLinks(CommandTestCase):
    def setUp(self):
        super().setUp()
        self.command = CheckBrokenLinksCommand

    def test_handle_response_code_successful(self):
        out = self.call_command("check_broken_links")
        self.assertIn("Deleted 0 old BrokenLinks.", out)

    def test_request_head_redirect_handling(self):
        # Simuleer response met een redirect en een relatieve locatie
        # Test case 1 - Successful request with default response
        sample_url_1 = "https://example.com"
        response_1 = self.command.request_head(self=self.command, url=sample_url_1)
        self.assertEqual(response_1.status_code, 200)

        # Test case 2 - Successful request to Google
        sample_url_2 = "https://google.com"
        response_2 = self.command.request_head(self=self.command, url=sample_url_2)
        self.assertEqual(response_2.status_code, 200)

        # Test case 3 - Multiple redirects, final status 200
        sample_url_3 = "https://digid.nl/inloggen"
        response_3 = self.command.request_head(self=self.command, url=sample_url_3)
        self.assertEqual(response_3.status_code, 200)

        # Test case 4 - 301 Redirect
        sample_url_4 = "https://httpbin.org/status/301"
        response_4 = self.command.request_head(self=self.command, url=sample_url_4)
        self.assertEqual(response_4.status_code, 200)

        # Test case 5 - 302 Redirect
        sample_url_5 = "https://httpbin.org/status/302"
        response_5 = self.command.request_head(self=self.command, url=sample_url_5)
        self.assertEqual(response_5.status_code, 200)

        # Test case 6 - 303 Redirect
        sample_url_6 = "https://httpbin.org/status/303"
        response_6 = self.command.request_head(self=self.command, url=sample_url_6)
        self.assertEqual(response_6.status_code, 200)

        # Test case 7 - 308 Redirect
        sample_url_7 = (
            "https://www.zoetermeer.nl/verhuizen-naar-het-buitenland-emigreren/"
        )
        response_7 = self.command.request_head(self=self.command, url=sample_url_7)
        self.assertEqual(response_7.status_code, 200)

        # Test case 8 - Invalid or unknown status code 309
        sample_url_8 = "https://httpbin.org/status/309"
        response_8 = self.command.request_head(self=self.command, url=sample_url_8)
        self.assertNotEqual(
            response_8.status_code, 200
        )  # Expect not 200 for unknown redirect status

        # Test case 9 - 404 Not Found
        sample_url_9 = "https://www.google.com/404"
        response_9 = self.command.request_head(self=self.command, url=sample_url_9)
        self.assertEqual(response_9.status_code, 404)

        # Test case 10 - URL without protocol (should raise an error or handle gracefully)
        sample_url_10 = "www.google.com"
        response_10 = self.command.request_head(self=self.command, url=sample_url_10)
        self.assertEqual(response_10.status_code, 200)

        # Test case 11 - Server Error 500
        sample_url_11 = "https://httpbin.org/status/500"
        response_11 = self.command.request_head(self=self.command, url=sample_url_11)
        self.assertEqual(response_11.status_code, 500)

        # Test case 12 - Client Error 403
        sample_url_12 = "https://httpbin.org/status/403"
        response_12 = self.command.request_head(self=self.command, url=sample_url_12)
        self.assertEqual(response_12.status_code, 403)

    @patch("sdg.producten.models.BrokenLinks.objects.exclude")
    def test_clean_up_removed_urls(self, mock_exclude):
        # Simuleer oude broken links die niet meer voorkomen
        mock_queryset = MagicMock()
        mock_exclude.return_value = mock_queryset
        mock_queryset.__len__.return_value = 2  # Twee items om te verwijderen

        out = self.call_command("check_broken_links")
        self.assertIn("Deleted 2 old BrokenLinks", out)

    @patch("sdg.producten.models.Product.objects.exclude_generic_status")
    @patch("sdg.producten.models.LocalizedProduct.objects.filter")
    def test_handle_method(self, mock_localized_filter, mock_product_queryset):
        # Simuleer een Product queryset en LocalizedProduct queryset
        mock_product = MagicMock()
        mock_product_queryset.return_value = [mock_product]
        mock_localized = MagicMock()
        mock_localized_filter.return_value = [mock_localized]

        # Roep handle aan met een reset
        with patch(
            "sdg.producten.models.BrokenLinks.objects.all"
        ) as mock_broken_links_all:
            mock_broken_links = MagicMock()
            mock_broken_links_all.return_value = [mock_broken_links]

            out = self.call_command("check_broken_links", "--reset")
            self.assertIn(
                "Succesfully cleared the error_count of every BrokenLink.", out
            )

            # Controleer dat de reset werd uitgevoerd
            mock_broken_links.reset_error_count.assert_called_once()

import os
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

import requests_mock

from sdg.core.constants import PublicData, TaalChoices
from sdg.core.models import Informatiegebied, Overheidsorganisatie, UniformeProductnaam
from sdg.core.tests.data import binary
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import ThemaFactory, UniformeProductnaamFactory
from sdg.producten.tests.factories.product import GeneriekProductFactory

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
    def test_load_gemeenten(self):
        out = self.call_command(
            "load_gemeenten", os.path.join(TESTS_DIR, "data/Gemeente.xml")
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(5 objects)", out)
        self.assertEqual(5, Overheidsorganisatie.objects.count())

        organisatie = Overheidsorganisatie.objects.first()
        self.assertEqual(organisatie.owms_pref_label, "'s-Graveland")
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/'s-Graveland_(gemeente)",
            organisatie.owms_identifier,
        )
        self.assertEqual(datetime(2001, 12, 31), organisatie.owms_end_date)

    def test_load_informatiegebieden(self):
        out = self.call_command(
            "load_informatiegebieden",
            os.path.join(TESTS_DIR, "data/SDG-Informatiegebieden.csv"),
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(24 objects)", out)
        self.assertEqual(24, Informatiegebied.objects.count())

        informatiegebied = Informatiegebied.objects.first()
        self.assertEqual(informatiegebied.code, "A1")
        self.assertEqual(informatiegebied.informatiegebied, "Reizen binnen de Unie")
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/sdg_reizUnie",
            informatiegebied.informatiegebied_uri,
        )

    def test_load_upn(self):
        thema_1 = ThemaFactory.create(informatiegebied__code="A1")
        ThemaFactory.create(informatiegebied__code="L2")
        out = self.call_command(
            "load_upn", os.path.join(TESTS_DIR, "data/UPL-actueel.csv")
        )

        self.assertIn("Successfully imported", out)
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
        self.assertEqual(2, upn.generieke_producten.count())
        first_generic = upn.generieke_producten.first()
        self.assertEqual("eu-burger", first_generic.doelgroep)
        self.assertEqual("eu-bedrijf", upn.generieke_producten.last().doelgroep)
        self.assertEqual(len(TaalChoices), first_generic.vertalingen.count())

    @requests_mock.Mocker()
    def test_load_gemeenten_from_url(self, m):
        m.get(PublicData.GEMEENTE.value, content=binary.GEMEENTE)
        out = self.call_command("load_gemeenten", PublicData.GEMEENTE.value)

        self.assertIn("Successfully imported", out)
        self.assertIn("(5 objects)", out)
        self.assertEqual(5, Overheidsorganisatie.objects.count())

        organisatie = Overheidsorganisatie.objects.first()
        self.assertEqual("'s-Graveland", organisatie.owms_pref_label)
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/'s-Graveland_(gemeente)",
            organisatie.owms_identifier,
        )
        self.assertEqual(datetime(2001, 12, 31), organisatie.owms_end_date)

    @requests_mock.Mocker()
    def test_load_informatiegebieden_from_url(self, m):
        m.get(PublicData.INFORMATIEGEBIED.value, content=binary.INFORMATIEGEBIED)
        out = self.call_command(
            "load_informatiegebieden", PublicData.INFORMATIEGEBIED.value
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(14 objects)", out)
        self.assertEqual(14, Informatiegebied.objects.count())

        informatiegebied = Informatiegebied.objects.first()
        self.assertEqual("A1", informatiegebied.code)
        self.assertEqual("Reizen binnen de Unie", informatiegebied.informatiegebied)
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/sdg_reizUnie",
            informatiegebied.informatiegebied_uri,
        )

    @requests_mock.Mocker()
    def test_load_upn_from_url(self, m):
        m.get(PublicData.UPN.value, content=binary.UPN)
        out = self.call_command("load_upn", PublicData.UPN.value)

        self.assertIn("Successfully imported", out)
        self.assertIn("(16 objects)", out)
        self.assertEqual(16, UniformeProductnaam.objects.count())

        upn = UniformeProductnaam.objects.first()
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
            upn.upn_uri,
        )
        self.assertEqual("aanleunwoning", upn.upn_label)
        self.assertEqual(False, upn.rijk)
        self.assertEqual(True, upn.burger)


class TestAutofill(CommandTestCase):
    def test_autofill_matching_with_generic(self):
        ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["provincie", "waterschap"],
            is_referentie_catalogus=True,
        )
        generic_product = GeneriekProductFactory.create(
            upn__provincie=True,
            upn__waterschap=True,
        )

        self.assertEqual(0, generic_product.producten.count())
        out = self.call_command("autofill")

        self.assertEqual(1, generic_product.producten.count())
        reference_product = generic_product.producten.get(
            referentie_product__isnull=True
        )
        self.assertEqual(1, reference_product.versies.count())
        reference_version = reference_product.versies.get()
        self.assertEqual(2, reference_version.vertalingen.count())
        self.assertIn("Created new product", out)

    def test_autofill_matching_without_generic(self):
        ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["provincie", "waterschap"],
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=True,
        )

        self.assertEqual(0, upn.generieke_producten.count())
        out = self.call_command("autofill")

        self.assertEqual(1, upn.generieke_producten.count())
        generic_product = upn.generieke_producten.get()
        self.assertEqual(2, generic_product.vertalingen.count())
        self.assertIn("Created new generic product", out)

        self.assertEqual(1, generic_product.producten.count())
        reference_product = generic_product.producten.get(
            referentie_product__isnull=True
        )
        self.assertEqual(1, reference_product.versies.count())
        reference_version = reference_product.versies.get()
        self.assertEqual(2, reference_version.vertalingen.count())
        self.assertIn("Created new product", out)

    def test_autofill_catalog_not_matching(self):
        ProductenCatalogusFactory.create(
            autofill=True,
            autofill_upn_filter=["provincie", "waterschap"],
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=False,
        )

        self.call_command("autofill")
        self.assertEqual(1, upn.generieke_producten.count())

        generic_product = upn.generieke_producten.get()
        self.assertEqual(0, generic_product.producten.count())

    def test_non_autofill_catalog(self):
        ProductenCatalogusFactory.create(
            autofill=False,
            is_referentie_catalogus=True,
        )
        upn = UniformeProductnaamFactory.create(
            provincie=True,
            waterschap=False,
        )

        self.call_command("autofill")
        self.assertEqual(1, upn.generieke_producten.count())

        generic_product = upn.generieke_producten.get()
        self.assertEqual(0, generic_product.producten.count())

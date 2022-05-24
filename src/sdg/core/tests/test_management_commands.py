import os
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from sdg.core.constants import TaalChoices
from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import ThemaFactory, UniformeProductnaamFactory
from sdg.organisaties.models import LokaleOverheid
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
    def test_load_government_orgs(self):
        out = self.call_command(
            "load_government_orgs",
            os.path.join(TESTS_DIR, "data/Overheidsorganisatie.xml"),
        )

        self.assertIn("Successfully imported", out)
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
            "load_municipalities", os.path.join(TESTS_DIR, "data/Gemeente.xml")
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(0 objects)", out)
        self.assertEqual(0, Overheidsorganisatie.objects.count())

    def test_load_municipalities_after_gov_orgs(self):
        self.call_command(
            "load_government_orgs",
            os.path.join(TESTS_DIR, "data/Overheidsorganisatie.xml"),
        )

        out = self.call_command(
            "load_municipalities", os.path.join(TESTS_DIR, "data/Gemeente.xml")
        )

        self.assertIn("Successfully imported", out)
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

        self.assertIn("Successfully imported", out)
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
        first_generic = upn.generieke_producten.get(doelgroep="eu-burger")
        self.assertEqual("eu-burger", first_generic.doelgroep)
        self.assertEqual("eu-bedrijf", upn.generieke_producten.last().doelgroep)
        self.assertEqual(len(TaalChoices), first_generic.vertalingen.count())


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

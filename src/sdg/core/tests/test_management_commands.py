import os
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

import requests_mock

from sdg.core.constants import PublicData
from sdg.core.models import Informatiegebied, Overheidsorganisatie, UniformeProductnaam
from sdg.core.tests.data import binary

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
        out = self.call_command(
            "load_upn", os.path.join(TESTS_DIR, "data/UPL-actueel.csv")
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(18 objects)", out)
        self.assertEqual(UniformeProductnaam.objects.count(), 18)

        upn = UniformeProductnaam.objects.first()
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
            upn.upn_uri,
        )
        self.assertEqual("aanleunwoning", upn.upn_label)
        self.assertEqual(False, upn.rijk)
        self.assertEqual(True, upn.burger)

    def test_load_upn_informatiegebieden(self):
        self.call_command("load_upn", os.path.join(TESTS_DIR, "data/UPL-actueel.csv"))
        self.call_command(
            "load_informatiegebieden",
            os.path.join(TESTS_DIR, "data/SDG-Informatiegebieden.csv"),
        )
        out = self.call_command(
            "load_upn_informatiegebieden",
            os.path.join(TESTS_DIR, "data/UPL-SDG-Informatiegebied.csv"),
        )

        self.assertIn("Successfully imported", out)
        self.assertIn("(3 objects)", out)

        upn = UniformeProductnaam.objects.get(upn_label="adoptie")
        self.assertEqual(
            str(upn.thema.informatiegebied), "Burger- en familierechten [G1]"
        )

        upn = UniformeProductnaam.objects.get(
            upn_label="aanpassing zelfgebouwd vliegtuig melding"
        )
        self.assertEqual(str(upn.thema.informatiegebied), "Voertuigen in de Unie [C5]")

        upn = UniformeProductnaam.objects.get(upn_label="adoptie aangifte")
        self.assertEqual(
            str(upn.thema.informatiegebied), "Burger- en familierechten [G1]"
        )

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
        self.assertIn("(18 objects)", out)
        self.assertEqual(18, UniformeProductnaam.objects.count())

        upn = UniformeProductnaam.objects.first()
        self.assertEqual(
            "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
            upn.upn_uri,
        )
        self.assertEqual("aanleunwoning", upn.upn_label)
        self.assertEqual(False, upn.rijk)
        self.assertEqual(True, upn.burger)

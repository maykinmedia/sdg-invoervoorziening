import os
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from sdg.core.models import Informatiegebied, Overheidsorganisatie, UniformeProductnaam

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

        self.assertIn("Succesfully imported", out)
        self.assertIn("(5 objects)", out)
        self.assertEqual(Overheidsorganisatie.objects.count(), 5)

        organisatie = Overheidsorganisatie.objects.get(pk=1)
        self.assertEqual(organisatie.owms_pref_label, "'s-Graveland")
        self.assertEqual(
            organisatie.owms_identifier,
            "http://standaarden.overheid.nl/owms/terms/'s-Graveland_(gemeente)",
        )
        self.assertEqual(organisatie.owms_end_date, datetime(2001, 12, 31))

    def test_load_informatiegebieden(self):
        out = self.call_command(
            "load_informatiegebieden",
            os.path.join(TESTS_DIR, "data/SDG-Informatiegebieden.csv"),
        )

        self.assertIn("Succesfully imported", out)
        self.assertIn("(14 objects)", out)
        self.assertEqual(Informatiegebied.objects.count(), 14)

        informatiegebied = Informatiegebied.objects.get(pk=1)
        self.assertEqual(informatiegebied.code, "A1")
        self.assertEqual(informatiegebied.informatiegebied, "Reizen binnen de Unie")
        self.assertEqual(
            informatiegebied.informatiegebied_uri,
            "http://standaarden.overheid.nl/owms/terms/sdg_reizUnie",
        )

    def test_load_upn(self):
        out = self.call_command(
            "load_upn", os.path.join(TESTS_DIR, "data/UPL-actueel.csv")
        )

        self.assertIn("Succesfully imported", out)
        self.assertIn("(19 objects)", out)
        self.assertEqual(UniformeProductnaam.objects.count(), 19)

        upn = UniformeProductnaam.objects.get(pk=2)
        self.assertEqual(
            upn.upn_uri, "http://standaarden.overheid.nl/owms/terms/aanleunwoning"
        )
        self.assertEqual(upn.upn_label, "aanleunwoning")
        self.assertEqual(upn.rijk, False)
        self.assertEqual(upn.burger, True)

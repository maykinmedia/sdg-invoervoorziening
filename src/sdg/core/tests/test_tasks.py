from django.test import TestCase

from freezegun import freeze_time

from ..models import ApplicationRapport
from ..tasks import clean_application_exports, create_application_export
from .factories.export import ApplicationExportFactory


class CreateApplicationExportTestCase(TestCase):

    @freeze_time("2026-01-01T02:02:02Z")
    def test_create_rapport(self):
        export = ApplicationExportFactory.create()
        create_application_export(application_export_pk=export.pk)
        export.refresh_from_db()

        self.assertTrue(export.file)
        file_name = export.file.name.split("/")[-1]
        self.assertIn("application_rapport_2026-01-01T02-02-02", file_name)


class CleanApplicationExportTestCase(TestCase):
    def test_clean_exports(self):
        with freeze_time("2026-01-01"):
            old_rapport = ApplicationExportFactory.create().pk

        with freeze_time("2026-03-02"):
            thirty_day_old_rapport = ApplicationExportFactory.create().pk

        with freeze_time("2026-04-01"):
            new_rapport = ApplicationExportFactory.create().pk
            clean_application_exports()

        existing_rapports = ApplicationRapport.objects.values_list("pk", flat=True)

        self.assertNotIn(old_rapport, existing_rapports)
        self.assertIn(new_rapport, existing_rapports)
        self.assertIn(thirty_day_old_rapport, existing_rapports)

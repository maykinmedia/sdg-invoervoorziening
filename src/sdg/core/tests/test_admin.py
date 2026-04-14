import datetime
import io
from unittest.mock import MagicMock, patch

from django.core.files import File
from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest
from freezegun import freeze_time
from maykin_2fa.test import disable_admin_mfa

from sdg.accounts.tests.factories import SuperUserFactory

from ..models import ApplicationRapport
from .factories.export import ApplicationExportFactory


@disable_admin_mfa()
class TestApplicationExportAdmin(WebTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = SuperUserFactory.create()

    def test_change_page_show_elements(self):
        ApplicationExportFactory.create_batch(2)

        response = self.app.get(
            reverse("admin:core_applicationrapport_changelist"),
            user=self.user,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-gemaakt_op", 2)

    @freeze_time("2026-01-01")
    def test_show_export_not_finished(self):
        ApplicationExportFactory.create()

        response = self.app.get(
            reverse("admin:core_applicationrapport_changelist"),
            user=self.user,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("bezig..."), 1)
        self.assertContains(response, _("Download rapport"), 0)

    @freeze_time("2026-01-01")
    def test_show_export_finished(self):
        ApplicationExportFactory.create(
            file=File(file=io.BytesIO(b"test"), name="test.xlsx"),
        )

        response = self.app.get(
            reverse("admin:core_applicationrapport_changelist"),
            user=self.user,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("compleet"), 1)
        self.assertContains(response, _("Download rapport"), 1)

        with self.subTest("download_export"):
            download = response.click(description=_("Download rapport"))
            self.assertTrue(download.content_disposition)

    @freeze_time("2026-01-01T00:00:00Z")
    @patch("sdg.core.tasks.create_application_export.delay")
    def test_export(self, mock_export_task: MagicMock):
        assert ApplicationRapport.objects.count() == 0

        response = self.app.get(
            reverse("admin:core_applicationrapport_changelist"),
            user=self.user,
        )

        self.assertEqual(response.status_code, 200)

        with self.captureOnCommitCallbacks(execute=True):
            export_response = response.click(
                description=_("Exporteer statistieken")
            ).follow()

        self.assertEqual(export_response.status_code, 200)
        self.assertContains(export_response, "field-gemaakt_op", 1)
        self.assertContains(
            export_response,
            _(
                "Het rapport wordt ge-exporteert, "
                "u kunt hem binnen enkele minuten hier vinden/downloaden."
            ),
        )
        export = ApplicationRapport.objects.get()
        self.assertTrue(export.gemaakt_op, datetime.datetime(2026, 1, 1, 0, 0, 0))
        mock_export_task.assert_called_once_with(application_export_pk=export.pk)

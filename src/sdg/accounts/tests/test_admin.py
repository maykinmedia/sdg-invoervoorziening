from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest

from sdg.tests.utils import disable_2fa

from ..models import UserInvitation
from .factories import SuperUserFactory


@disable_2fa
class AdminTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.user_add_url = reverse("admin:accounts_user_add")

    def setUp(self):
        super().setUp()
        self.app.set_user(self.user)

    @override_settings(SDG_ORGANIZATION_TYPE="municipality")
    def test_invitation_email_is_sent_after_creating_user(self):
        response = self.app.get(self.user_add_url)

        response.form["email"] = "test@example.com"
        response.form["first_name"] = "Arthur"
        response.form["last_name"] = "Dent"
        response.form.submit()

        self.assertEqual(len(mail.outbox), 1)

        invite = UserInvitation.objects.get()
        self.assertEqual(
            mail.outbox[0].subject,
            settings.INVITATION_SUBJECT.format(org_type_name_plural=_("gemeenten")),
        )
        self.assertIn(
            "Arthur Dent",
            mail.outbox[0].body,
        )
        self.assertIn(
            invite.key,
            mail.outbox[0].body,
        )

from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa as disable_mfa

from ..models import UserInvitation
from .factories import SuperUserFactory


@disable_mfa()
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

        form = response.forms["user_form"]
        form["email"] = "test@example.com"
        form["first_name"] = "Arthur"
        form["last_name"] = "Dent"
        form.submit()

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

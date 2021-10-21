from django.conf import settings
from django.core import mail
from django.urls import reverse

from django_webtest import WebTest

from ..models import UserInvitation
from .factories import SuperUserFactory


class AdminTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = SuperUserFactory.create()
        self.app.set_user(self.user)

    def test_invitation_email_is_sent_after_creating_user(self):
        response = self.app.get(reverse("admin:accounts_user_add"))

        response.form["email"] = "test@example.com"
        response.form["first_name"] = "Arthur"
        response.form["last_name"] = "Dent"
        response.form.submit()

        self.assertEqual(len(mail.outbox), 1)

        invite = UserInvitation.objects.get()
        self.assertEqual(mail.outbox[0].subject, settings.INVITATION_SUBJECT)
        self.assertIn(
            "Arthur Dent",
            mail.outbox[0].body,
        )
        self.assertIn(
            invite.key,
            mail.outbox[0].body,
        )

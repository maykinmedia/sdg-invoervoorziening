from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from django_webtest import WebTest

from sdg.accounts.models import UserInvitation
from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory

INVITATION_URL = "organisaties:roles:invitation_create"
INVITATION_ACCEPT_URL = "invitation_accept"

User = get_user_model()


class InvitationTests(WebTest):
    def setUp(self):
        super().setUp()

        self.lokale_overheid = LokaleOverheidFactory.create()

        self.manager_user = UserFactory.create()
        self.manager_role = RoleFactory.create(
            user=self.manager_user,
            lokale_overheid=self.lokale_overheid,
            is_beheerder=True,
        )
        self.app.set_user(self.manager_user)

    @staticmethod
    def _fill_invitation_form(form):
        form["email"] = "test@example.com"
        form["first_name"] = "Arthur"
        form["last_name"] = "Dent"
        form["form-0-is_beheerder"] = False
        form["form-0-is_redacteur"] = True

    def test_manager_can_create_invitation(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )

        self.assertEqual(User.objects.count(), 1)

        self._fill_invitation_form(response.form)
        response.form.submit()

        self.assertEqual(User.objects.count(), 2)

        role = self.lokale_overheid.roles.get(user__email="test@example.com")
        self.assertEqual(role.is_redacteur, True)
        self.assertEqual(role.is_beheerder, False)

    def test_manager_can_create_invitation_for_existing_user(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )
        self.extra_user = UserFactory.create(email="test@example.com")
        self.assertEqual(User.objects.count(), 2)

        self._fill_invitation_form(response.form)
        response.form.submit()

        self.assertEqual(User.objects.count(), 2)

        role = self.lokale_overheid.roles.get(user__email="test@example.com")
        self.assertEqual(role.is_redacteur, True)
        self.assertEqual(role.is_beheerder, False)

    def test_editor_cannot_create_invitation(self):
        editor_user = UserFactory.create()
        RoleFactory.create(
            user=editor_user,
            lokale_overheid=self.lokale_overheid,
            is_redacteur=True,
        )
        self.app.set_user(editor_user)
        self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk}), status=403
        )

    def test_invitation_email_is_sent(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )

        self._fill_invitation_form(response.form)
        response.form.submit()

        self.assertEqual(len(mail.outbox), 1)

    def test_invitation_template_is_correct(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )

        self._fill_invitation_form(response.form)
        response.form.submit()

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

    def test_can_accept_invitation(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )
        self._fill_invitation_form(response.form)
        response.form.submit()

        invite = UserInvitation.objects.get()
        response = self.app.get(
            reverse(INVITATION_ACCEPT_URL, kwargs={"key": invite.key})
        )
        response.form["password"] = "Test@1234"
        response.form["password_confirm"] = "Test@1234"
        response.form.submit()

        invite.refresh_from_db()

        user = User.objects.get(email="test@example.com")
        self.assertEqual(invite.accepted, True)
        self.assertEqual(user.check_password("Test@1234"), True)

    def test_cannot_accept_invitation_with_invalid_key(self):
        response = self.app.get(
            reverse(INVITATION_URL, kwargs={"pk": self.lokale_overheid.pk})
        )
        self._fill_invitation_form(response.form)
        response.form.submit()

        self.app.get(
            reverse(INVITATION_ACCEPT_URL, kwargs={"key": "random1234"}),
            status=404,
        )

from django.urls import reverse_lazy

from django_webtest import WebTest

from sdg.accounts.models import Role
from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory


class RoleTests(WebTest):
    def setUp(self):
        super().setUp()

        self.lokale_overheid = LokaleOverheidFactory.create()

        self.manager_user = UserFactory.create()
        self.editor_user = UserFactory.create()

        self.manager_role = RoleFactory.create(
            user=self.manager_user,
            lokale_overheid=self.lokale_overheid,
            is_beheerder=True,
        )
        self.editor_role = RoleFactory.create(
            user=self.editor_user,
            lokale_overheid=self.lokale_overheid,
            is_redacteur=True,
        )

    def test_delete_url_is_displayed_for_manager(self):
        self.app.set_user(self.manager_user)
        response = self.app.get(self.manager_role.get_absolute_url())
        delete_url = reverse_lazy(
            "organisaties:overheid_role_delete",
            kwargs={"pk": self.lokale_overheid.pk, "role_pk": self.editor_role.pk},
        )
        self.assertIn(
            str(delete_url),
            response.text,
        )

    def test_delete_url_is_not_displayed_for_editor(self):
        self.app.set_user(self.editor_user)
        response = self.app.get(self.manager_role.get_absolute_url())
        delete_url = reverse_lazy(
            "organisaties:overheid_role_delete",
            kwargs={"pk": self.lokale_overheid.pk, "role_pk": self.manager_role.pk},
        )
        self.assertNotIn(
            str(delete_url),
            response.text,
        )

    def test_manager_can_delete_roles(self):
        self.app.set_user(self.manager_user)
        self.assertEqual(Role.objects.count(), 2)

        delete_url = reverse_lazy(
            "organisaties:overheid_role_delete",
            kwargs={"pk": self.lokale_overheid.pk, "role_pk": self.editor_role.pk},
        )
        response = self.app.get(delete_url)
        response.form.submit()

        self.assertEqual(Role.objects.count(), 1)

    def test_editor_cannot_delete_roles(self):
        self.app.set_user(self.editor_user)
        self.assertEqual(Role.objects.count(), 2)

        delete_url = reverse_lazy(
            "organisaties:overheid_role_delete",
            kwargs={"pk": self.lokale_overheid.pk, "role_pk": self.manager_role.pk},
        )
        self.app.get(delete_url, status=403)

        self.assertEqual(Role.objects.count(), 2)

    def test_manager_cannot_delete_own_role(self):
        self.app.set_user(self.manager_user)
        self.assertEqual(Role.objects.count(), 2)

        delete_url = reverse_lazy(
            "organisaties:overheid_role_delete",
            kwargs={"pk": self.lokale_overheid.pk, "role_pk": self.manager_role.pk},
        )
        self.app.get(delete_url, status=403)

        self.assertEqual(Role.objects.count(), 2)

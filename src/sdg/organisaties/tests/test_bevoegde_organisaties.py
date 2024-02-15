from django.urls import reverse_lazy

from sdg.core.tests.utils import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory


class BevoedgeOrganisatieUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.lokale_overheid = LokaleOverheidFactory.create()
        self.org = OverheidsorganisatieFactory.create()

        self.manager_user = UserFactory.create()

        RoleFactory.create(
            user=self.manager_user,
            lokale_overheid=self.lokale_overheid,
            is_beheerder=True,
        )

    def test_update_authorized_organizations(self):
        self.app.set_user(self.manager_user)
        url = reverse_lazy(
            "organisaties:bevoegde_organisaties",
            kwargs={"pk": self.lokale_overheid.pk},
        )

        response = self.app.get(url)
        csrf_token = response.form["csrfmiddlewaretoken"].value

        response = self.app.post(
            url,
            params={
                "csrfmiddlewaretoken": csrf_token,
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 0,
                "form-MIN_NUM_FORMS": 0,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-lokale-overheid": self.lokale_overheid.pk,
                "form-0-organisatie": self.org.pk,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.lokale_overheid.bevoegde_organisaties.count(), 1)
        authorized_org = self.lokale_overheid.bevoegde_organisaties.first()

        self.assertEqual(authorized_org.lokale_overheid, self.lokale_overheid)
        self.assertEqual(authorized_org.organisatie, self.org)
        self.assertEqual(authorized_org.naam, self.org.owms_pref_label)

    def test_update_authorized_organizations_not_in_the_list_marked(self):
        self.app.set_user(self.manager_user)
        url = reverse_lazy(
            "organisaties:bevoegde_organisaties",
            kwargs={"pk": self.lokale_overheid.pk},
        )

        response = self.app.get(url)
        csrf_token = response.form["csrfmiddlewaretoken"].value

        response = self.app.post(
            url,
            params={
                "csrfmiddlewaretoken": csrf_token,
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 0,
                "form-MIN_NUM_FORMS": 0,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-lokale-overheid": self.lokale_overheid.pk,
                "form-0-organisatie": self.org.pk,
                "form-0-staat_niet_in_de_lijst": True,
                "form-0-naam": "test",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.lokale_overheid.bevoegde_organisaties.count(), 1)
        authorized_org = self.lokale_overheid.bevoegde_organisaties.first()

        self.assertEqual(authorized_org.lokale_overheid, self.lokale_overheid)
        self.assertEqual(authorized_org.organisatie, self.org)
        self.assertEqual(authorized_org.naam, self.org.owms_pref_label)

    def test_update_authorized_organizations_empty_organization(self):
        self.app.set_user(self.manager_user)
        url = reverse_lazy(
            "organisaties:bevoegde_organisaties",
            kwargs={"pk": self.lokale_overheid.pk},
        )

        response = self.app.get(url)
        csrf_token = response.form["csrfmiddlewaretoken"].value

        response = self.app.post(
            url,
            params={
                "csrfmiddlewaretoken": csrf_token,
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 0,
                "form-MIN_NUM_FORMS": 0,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-lokale-overheid": self.lokale_overheid.pk,
                "form-0-staat_niet_in_de_lijst": True,
                "form-0-naam": "test",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.lokale_overheid.bevoegde_organisaties.count(), 1)
        authorized_org = self.lokale_overheid.bevoegde_organisaties.first()

        self.assertEqual(authorized_org.lokale_overheid, self.lokale_overheid)
        self.assertIsNone(authorized_org.organisatie)
        self.assertEqual(authorized_org.naam, "test")

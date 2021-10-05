from django.urls import reverse_lazy

from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.constants import Status

HOME_URL = "core:home"
CARD_CLASS_NAME = ".cards__card"


class HomeViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_only_allowed_municipalities_are_displayed(self):
        role1 = RoleFactory.create(user=self.user)
        role2 = RoleFactory.create(user=self.user)
        RoleFactory.create()
        RoleFactory.create()

        response = self.app.get(reverse_lazy(HOME_URL))
        self.assertEqual(response.status_code, Status.OK)

        municipalities = response.pyquery(CARD_CLASS_NAME)

        self.assertEqual(len(municipalities), 2)

        self.assertEqual(
            municipalities[0].text_content().strip(), str(role1.lokale_overheid)
        )
        self.assertEqual(
            municipalities[1].text_content().strip(), str(role2.lokale_overheid)
        )
        self.assertEqual(
            municipalities[0].attrib["href"],
            role1.lokale_overheid.get_absolute_url(),
        )

    def test_real_name_is_displayed(self):
        response = self.app.get(reverse_lazy(HOME_URL))
        self.assertEqual(response.status_code, Status.OK)
        self.assertIn(
            self.user.get_full_name(),
            response.text,
        )

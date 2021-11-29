from django.urls import reverse

from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory

HOME_URL = "core:home"
CARD_SELECTOR = ".cards__card"


class HomeViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_only_allowed_municipalities_are_displayed(self):
        role1, role2 = RoleFactory.create_batch(2, user=self.user, is_redacteur=True)
        RoleFactory.create_batch(3)

        response = self.app.get(reverse(HOME_URL))

        municipalities = response.pyquery(CARD_SELECTOR)

        self.assertEqual(municipalities.length, 2)

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
        response = self.app.get(reverse(HOME_URL))
        self.assertIn(self.user.get_full_name(), response.text)

    def test_redirect_to_municipality_if_user_has_only_role(self):
        role = RoleFactory.create(user=self.user, is_redacteur=True)
        response = self.app.get(reverse(HOME_URL), auto_follow=True)
        self.assertEqual(role.lokale_overheid.get_absolute_url(), response.request.path)

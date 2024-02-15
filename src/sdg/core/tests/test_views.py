from django.test import override_settings
from django.urls import reverse

from sdg.core.tests.utils import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.conf.utils import org_type_cfg

HOME_URL = "core:home"
CARD_SELECTOR = ".cards__card"


class HomeViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)
        org_type_cfg.cache_clear()

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

    def test_consultant_user_can_visit_home_page(self):
        RoleFactory.create(user=self.user, is_raadpleger=True)
        response = self.app.get(reverse(HOME_URL), auto_follow=True)
        self.assertEqual(200, response.status_code)

    @override_settings(SDG_ORGANIZATION_TYPE="waterauthority")
    def test_organization_type_link_is_displayed(self):
        response = self.app.get(reverse(HOME_URL))
        self.assertIn(str(org_type_cfg().url), response.text)

    @override_settings(SDG_ORGANIZATION_TYPE="waterauthority")
    def test_organization_type_logo_is_displayed(self):
        response = self.app.get(reverse(HOME_URL))
        self.assertIn(org_type_cfg().footer_logo, response.text)

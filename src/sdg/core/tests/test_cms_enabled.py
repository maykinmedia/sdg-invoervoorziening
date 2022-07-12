import uuid

import django
from django.test import override_settings

from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory


class CMSUrlsPathTest(WebTest):
    # return 0 if the url is valid, return 1 if the url is not valid
    def invalid_url_path_check(self, url):
        try:
            self.app.get(url)
            return 0
        except django.urls.exceptions.NoReverseMatch:
            return 1

    def setUp(self):
        super().setUp()

        self.email = "test@test.test"
        self.password = str(uuid.uuid4())

        self.user = UserFactory.create(email=self.email, password=self.password)
        self.app.set_user(self.user)

        self.organisatie = OverheidsorganisatieFactory.create(
            owms_end_date=None,
        )
        self.lokale_overheid = LokaleOverheidFactory.create(
            organisatie=self.organisatie
        )
        ProductenCatalogusFactory.create(lokale_overheid=self.lokale_overheid)

        RoleFactory.create(
            user=self.user,
            lokale_overheid=self.lokale_overheid,
            is_beheerder=True,
            is_redacteur=True,
        )

    def test_cms_enabled(self, invalid_urls=0):
        # enabled urls:
        invalid_urls += self.invalid_url_path_check("/cmsapi/")
        invalid_urls += self.invalid_url_path_check("/reset/done/")
        invalid_urls += self.invalid_url_path_check("/accounts/login/")
        invalid_urls += self.invalid_url_path_check(
            "/organizations/" + str(self.lokale_overheid.id) + "/productenlijst/"
        )
        invalid_urls += self.invalid_url_path_check("/?name=home/")
        invalid_urls += self.invalid_url_path_check("/two_factor/")
        invalid_urls += self.invalid_url_path_check("/admin/")
        invalid_urls += self.invalid_url_path_check("/api/v1/")

        self.assertEqual(invalid_urls, 0)

    @override_settings(ROOT_URLCONF="sdg.cms_disabled_urls")
    def test_cms_disabled(self, invalid_urls=0):
        # disabled urls:
        invalid_urls += self.invalid_url_path_check("/cmsapi/")
        invalid_urls += self.invalid_url_path_check("/reset/done/")
        invalid_urls += self.invalid_url_path_check("/accounts/login/")
        invalid_urls += self.invalid_url_path_check(
            "/organizations/" + str(self.lokale_overheid.id) + "/productenlijst/"
        )
        invalid_urls += self.invalid_url_path_check("/?name=home/")
        invalid_urls += self.invalid_url_path_check("/two_factor/")
        invalid_urls += self.invalid_url_path_check("/admin/")

        # enabled urls:
        invalid_urls += self.invalid_url_path_check("/api/v1/")

        self.assertEqual(invalid_urls, 6)

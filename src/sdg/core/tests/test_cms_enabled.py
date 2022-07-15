import uuid

import django
from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, SuperUserFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory
from sdg.tests.utils import disable_2fa


@disable_2fa
class CMSUrlsPathTest(WebTest):
    def setUp(self):
        super().setUp()

        self.email = "test@test.test"
        self.password = str(uuid.uuid4())

        self.user = SuperUserFactory.create(email=self.email, password=self.password)
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

    def test_cms_enabled(self):
        cmsapi = self.app.get(reverse("cmsapi:api-root"), status="*")
        reset = self.app.get(reverse("password_reset_complete"), status="*")
        account = self.app.get(reverse("account_login"), status="*")
        organizations = self.app.get(
            reverse("organisaties:roles:list", args=[str(self.lokale_overheid.id)]),
            status="*",
        )
        home = self.app.get(reverse("core:home"), status="*")
        two_factor = self.app.get(reverse("two_factor:profile"), status="*")
        admin = self.app.get(reverse("admin:index"), status="*")
        api = self.app.get(reverse("api:api-root"), status="*")

        self.assertEqual(cmsapi.status_code, 200)
        self.assertEqual(reset.status_code, 200)
        self.assertEqual(account.status_code, 302)
        self.assertEqual(organizations.status_code, 200)
        self.assertEqual(home.status_code, 302)
        self.assertEqual(two_factor.status_code, 200)
        self.assertEqual(admin.status_code, 200)
        self.assertEqual(api.status_code, 200)

    @override_settings(SDG_CMS_ENABLED=False)
    @override_settings(ROOT_URLCONF="sdg.urls")
    def test_cms_disabled(self):
        cmsapi = self.app.get(reverse("cmsapi:api-root"), status="*")
        reset = self.app.get(reverse("password_reset_complete"), status="*")
        account = self.app.get(reverse("account_login"), status="*")
        organizations = self.app.get(
            reverse("organisaties:roles:list", args=[str(self.lokale_overheid.id)]),
            status="*",
        )
        home = self.app.get(reverse("core:home"), status="*")
        two_factor = self.app.get(reverse("two_factor:profile"), status="*")
        admin = self.app.get(reverse("admin:index"), status="*")
        api = self.app.get(reverse("api:api-root"), status="*")

        # disabled
        self.assertEqual(cmsapi.status_code, 404)
        self.assertEqual(reset.status_code, 404)
        self.assertEqual(account.status_code, 404)
        self.assertEqual(organizations.status_code, 404)
        self.assertEqual(home.status_code, 404)
        self.assertEqual(two_factor.status_code, 404)

        # enabled
        self.assertEqual(admin.status_code, 200)
        self.assertEqual(api.status_code, 200)

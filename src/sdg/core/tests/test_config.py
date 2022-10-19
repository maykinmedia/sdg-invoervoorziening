from django_webtest import WebTest

from sdg.accounts.tests.factories import UserFactory
from sdg.core.models import SiteConfiguration


class SiteConfigurationTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_custom_documentation_link(self):
        response = self.app.get("/")
        documentation_link = response.html.find("a", {"id": "documentation"})
        self.assertIsNone(documentation_link)

        siteconfig = SiteConfiguration.get_solo()
        siteconfig.documentatie_titel = "Documentation test"
        siteconfig.documentatie_link = "https://test.com"
        siteconfig.save()

        response = self.app.get("/")
        documentation_link = response.html.find("a", {"id": "documentation"})
        self.assertEqual(documentation_link["href"], "https://test.com")
        self.assertEqual(documentation_link.text.strip(), "Documentation test")

    def test_goatcounter_analytics(self):
        response = self.app.get("/")
        self.assertNotIn("data-goatcounter", response.text)

        siteconfig = SiteConfiguration.get_solo()
        siteconfig.goatcounter_domain = "example.com"
        siteconfig.save()

        response = self.app.get("/")
        self.assertInHTML(
            '<script data-goatcounter="https://example.com/count" async src="//example.com/count.js"></script>',
            response.text,
        )

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.utils import WebTest
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductFactory,
    SpecifiekProductFactory,
)

User = get_user_model()


class NotificatiesTests(WebTest):
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

    def test_notifications_list(self):
        reference_product = ReferentieProductFactory.create()
        specific_product = SpecifiekProductFactory.create()
        reference_versions = ProductVersieFactory.create_batch(
            5, product=reference_product, publicatie_datum=now()
        )
        specific_versions = ProductVersieFactory.create_batch(
            5, product=specific_product, publicatie_datum=now()
        )

        url = reverse("notificaties")
        response = self.app.get(url)

        notifications = response.pyquery("#notifications tbody tr")

        self.assertEqual(len(notifications), 5)

        for version in reference_versions:
            self.assertIn(str(version.product), response.text)

        for version in specific_versions:
            self.assertNotIn(str(version.product), response.text)

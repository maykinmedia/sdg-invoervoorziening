from unittest.mock import Mock

from django.core import mail
from django.urls import reverse

from django_webtest import WebTest

from sdg.accounts.tests.factories import SuperUserFactory
from sdg.core.events import event_register
from sdg.core.tests.utils import patch_event_register
from sdg.tests.utils import disable_2fa


@disable_2fa
class AdminTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.user_add_url = reverse("admin:accounts_user_add")

    def setUp(self):
        super().setUp()
        self.app.set_user(self.user)

    def test_custom_invitation_error_message_admin(self):
        with patch_event_register():
            mock_function = Mock()
            mock_function.side_effect = Exception("Boom")
            mock_function.admin_message = "Custom admin message"
            event_register["save_user"] = [mock_function]

            response = self.app.get(self.user_add_url)

            response.form["email"] = "test@example.com"
            response.form["first_name"] = "Arthur"
            response.form["last_name"] = "Dent"
            response = response.form.submit()

            self.assertEqual(len(mail.outbox), 0)

            response = response.follow()
            self.assertIn("Custom admin message", response)

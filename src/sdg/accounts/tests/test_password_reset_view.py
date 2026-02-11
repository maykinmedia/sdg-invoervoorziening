from unittest import mock

from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest

from sdg.accounts.tests.factories import UserFactory


class PasswordResetViewTests(WebTest):
    def test_user_cant_access_the_password_reset_view_more_than_5_times(self):
        url = reverse("admin_password_reset")

        for i in range(5):
            response = self.app.get(url)
            self.assertEqual(response.status_code, 200)
            print(i)
        response = self.app.get(url, status=403)
        self.assertEqual(response.status_code, 403)

    @mock.patch("django.contrib.auth.forms.PasswordResetForm.send_mail")
    def test_reset_flow(self, mock_send_mail):

        user = UserFactory(password="ForgetfulPassword")

        # Login
        response = self.app.get(reverse("two_factor:login"))
        self.assertIn(reverse("account_reset_password"), response)

        # Reset
        response = self.app.get(reverse("account_reset_password"))
        form = response.form
        form["email"] = user.email
        response = form.submit()

        # Reset done
        self.assertEqual(response.status_code, 302)
        response = response.follow()
        self.assertIn(_("Wachtwoord reset e-mail"), response)

        # Reset Key
        email_context = mock_send_mail.call_args.args[2]
        reset_url = reverse(
            "password_reset_confirm",
            args=[email_context["uid"], email_context["token"]],
        )
        response = self.app.get(reset_url)
        self.assertEqual(response.status_code, 302)

        # Reset Form
        response = response.follow()
        self.assertIn(_("Wachtwoord reset"), response)
        form = response.form
        form["new_password1"] = "VeryStrongPassword"
        form["new_password2"] = "VeryStrongPassword"
        response = form.submit()

        # Reset Done
        self.assertEqual(response.status_code, 302)
        response = response.follow()
        self.assertIn(_("Uw wachtwoord is nu gewijzigd."), response)

        # Login with new password
        response = self.app.get(reverse("two_factor:login"))
        form = response.form
        form["auth-username"] = user.email
        form["auth-password"] = "VeryStrongPassword"
        response = form.submit()
        self.assertEqual(response.status_code, 302)

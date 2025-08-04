from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.shortcuts import redirect
from django.views.generic import TemplateView

from allauth.account.utils import get_next_redirect_url
from allauth.account.views import RedirectAuthenticatedUserMixin
from two_factor.views import LoginView as _LoginView


class LoginDashboardView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = "account/login_dashboard.html"
    success_url = None
    redirect_field_name = "next"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "/")
        return self.render_to_response(context)

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(self.request, self.redirect_field_name)
            or self.success_url
        )
        return ret


class LoginView(_LoginView):
    # template_name = "account/login.html"
    # Overwrite the default two_factor LoginView to disable the 2fa step
    # when the setting DISABLE_2FA is set to True.
    # important to note that only accounts without devices will have the 2fa step
    # disabled, when a device is set the step will still take place.
    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        user = self.get_user()
        backends_to_skip_verification_for = getattr(
            settings, "MAYKIN_2FA_ALLOW_MFA_BYPASS_BACKENDS", []
        )

        login(self.request, user)
        device = getattr(self.get_user(), "otp_device", None)

        if not device and user.backend in backends_to_skip_verification_for:
            return redirect(self.get_success_url())

        return super().done(form_list, **kwargs)


class LogoutView(AuthLogoutView):
    http_method_names = ["get", "post"]
    template_name = "account/logout.html"

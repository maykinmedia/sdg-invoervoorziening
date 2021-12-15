from django.views.generic import TemplateView

from allauth.account.utils import get_next_redirect_url
from allauth.account.views import RedirectAuthenticatedUserMixin
from two_factor.views import LoginView as _LoginView

from sdg.accounts.forms import AuthenticationForm


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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form_list["auth"] = AuthenticationForm

from django.views.generic import TemplateView

from allauth.account.utils import get_next_redirect_url
from allauth.account.views import RedirectAuthenticatedUserMixin


class LoginDashboardView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = "account/login_dashboard.html"
    success_url = None
    redirect_field_name = "next"

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(self.request, self.redirect_field_name)
            or self.success_url
        )
        return ret

from django.contrib.auth import user_login_failed
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from allauth.account.utils import get_next_redirect_url
from allauth.account.views import RedirectAuthenticatedUserMixin
from axes.decorators import axes_dispatch, axes_form_invalid
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

    @method_decorator(axes_dispatch)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(axes_form_invalid)
    def _form_invalid(self, *args, **kwargs):
        """
        Method called when a form is invalid (django-axes compat)
        Ensure that the user_login_failed signal is sent when a token is invalid.
        """
        if self.request.POST.get("login_view-current_step") == "token":
            user_login_failed.send(
                sender=__name__,
                credentials={
                    "username": self.storage.authenticated_user.get_username(),
                },
                request=self.request,
            )

    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        if not form.is_valid():
            self._form_invalid(self)

        return response

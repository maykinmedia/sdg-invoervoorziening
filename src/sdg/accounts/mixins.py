from abc import ABC, abstractmethod

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from two_factor.views import OTPRequiredMixin

from sdg.accounts.models import Role

if getattr(settings, "TWO_FACTOR_FORCE_OTP", True):
    VerificationMixin = OTPRequiredMixin
else:
    VerificationMixin = LoginRequiredMixin


class BaseOverheidMixin(VerificationMixin, UserPassesTestMixin, ABC):
    _lokale_overheid = None

    def _get_lokale_overheid(self):
        if not self._lokale_overheid:
            self._lokale_overheid = self.get_lokale_overheid()

        return self._lokale_overheid

    def get_lokale_overheid(self):
        """
        :returns: The lokale overheid for which we are matching permissions for.
        """
        raise NotImplementedError(
            "{0} is missing the implementation of the get_lokale_overheid() method.".format(
                self.__class__.__name__
            )
        )

    @abstractmethod
    def test_func(self):
        return True


class OverheidRoleRequiredMixin(BaseOverheidMixin):
    """Ensures an authenticated user has a given list of role permissions."""

    required_roles = {i.name for i in Role.get_roles()}
    permission_denied_message = _(
        "U hebt niet de vereiste rol om deze pagina te openen."
    )

    def get_required_roles(self):
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Returns all roles by default.
        """
        return self.required_roles

    def test_func(self):
        _super = super()
        message = _super.__thisclass__.permission_denied_message
        if not _super.test_func():
            return False

        try:
            role = self.request.user.roles.get(
                lokale_overheid=self._get_lokale_overheid()
            )
        except Role.DoesNotExist:
            raise PermissionDenied(message)

        if not any(getattr(role, r) for r in self.get_required_roles()):
            raise PermissionDenied(message)

        return True


class OverheidExpirationMixin(BaseOverheidMixin):
    """Ensures a municipality view can no longer be access if the end date has passed."""

    permission_denied_message = _(
        "De einddatum van deze lokale overheid is verstreken en zij is niet langer toegankelijk."
    )

    def test_func(self):
        _super = super()
        if not _super.test_func():
            return False

        lokale_overheid = self._get_lokale_overheid()
        end_date = lokale_overheid.organisatie.owms_end_date

        if end_date and end_date <= now():
            raise PermissionDenied(_super.__thisclass__.permission_denied_message)
        return True


class OverheidContextMixin(BaseOverheidMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "lokaleoverheid" not in context:
            context["lokaleoverheid"] = self._get_lokale_overheid()

        return context


class OverheidMixin(
    OverheidContextMixin,
    OverheidExpirationMixin,
    OverheidRoleRequiredMixin,
):
    """
    The standard mixin for all municipality views.

    - Denies access if a municipality end date is expired.
    - Ensures a user has the appropriate role to access the municipality.
    - Add municipality to context if it doesn't already exist.
    """

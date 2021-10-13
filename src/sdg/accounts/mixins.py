from django.contrib.auth.mixins import UserPassesTestMixin

from two_factor.views import OTPRequiredMixin

from sdg.accounts.models import Role


class OverheidRoleRequiredMixin(OTPRequiredMixin, UserPassesTestMixin):
    """Ensures an authenticated user has a given list of role permissions."""

    required_roles = {i.name for i in Role.get_roles()}

    def get_lokale_overheid(self):
        """
        :returns: The lokale overheid for which we are matching permissions for.
        """
        raise NotImplementedError(
            "{0} is missing the implementation of the get_lokale_overheid() method.".format(
                self.__class__.__name__
            )
        )

    def get_required_roles(self):
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Returns all roles by default.
        """
        return self.required_roles

    def test_func(self):
        try:
            role = self.request.user.roles.get(
                lokale_overheid=self.get_lokale_overheid()
            )
        except Role.DoesNotExist:
            return False

        return any(getattr(role, r) for r in self.get_required_roles())

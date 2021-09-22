from abc import ABC

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from sdg.accounts.models import Role


class OverheidRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures an authenticated user has a given list of role permissions."""

    lokale_overheid = None
    required_roles = Role.get_allowed_roles()

    def get_lokale_overheid(self):
        """
        :returns: The lokale overheid for which we are matching permissions for.
        """
        return self.lokale_overheid

    def get_required_roles(self):
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Returns all roles by default.
        """
        return self.required_roles

    def test_func(self):
        try:
            role = self.request.user.roles.get(lokale_overheid=self.lokale_overheid)
        except Role.DoesNotExist:
            return False

        return all([getattr(role, r) for r in self.get_required_roles()])

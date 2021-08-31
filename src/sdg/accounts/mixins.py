from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

from sdg.accounts.models import Role


class OverheidRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures an authenticated user has a given list of role permissions."""

    lokale_overheid = None

    @staticmethod
    def get_required_roles():
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Returns all roles by default.
        """
        return Role.get_allowed_roles()

    def is_root_editor(self):
        """Check if the user has root editor privileges."""
        return getattr(self.request.user, "is_hoofdredacteur")

    def test_func(self):
        if self.is_root_editor():
            return True

        try:
            role = self.request.user.roles.get(lokale_overheid=self.lokale_overheid)
        except Role.DoesNotExist:
            return False

        return all([getattr(role, r) for r in self.get_required_roles()])

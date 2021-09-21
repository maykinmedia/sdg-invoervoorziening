from abc import ABC

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from sdg.accounts.models import Role


class RoleTestMixin(LoginRequiredMixin, UserPassesTestMixin, ABC):
    """Base class for role related permissions checks."""

    def is_root_editor(self):
        """Check if the user has root editor permission."""
        # TODO: Remove this since this is now a regular catalog feature.
        return True  # getattr(self.request.user, "is_hoofdredacteur")


class RootEditorRequiredMixin(RoleTestMixin):
    """Ensures an authenticated user has a root editor permissions."""

    def test_func(self):
        if self.is_root_editor():
            return True
        else:
            return False


class OverheidRoleRequiredMixin(RoleTestMixin):
    """Ensures an authenticated user has a given list of role permissions."""

    lokale_overheid = None

    def get_lokale_overheid(self):
        """
        :returns: The lokale overheid for which we are matching permissions for.
        """
        return self.lokale_overheid

    @staticmethod
    def get_required_roles():
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Returns all roles by default.
        """
        return Role.get_allowed_roles()

    def test_func(self):
        if self.is_root_editor():
            return True

        try:
            role = self.request.user.roles.get(lokale_overheid=self.lokale_overheid)
        except Role.DoesNotExist:
            return False

        return all([getattr(role, r) for r in self.get_required_roles()])

from abc import ABC, abstractmethod, abstractproperty

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class OverheidRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin, ABC):
    """Ensures an authenticated user has a given list of role permissions."""

    lokale_overheid = None

    @abstractmethod
    def get_required_roles(self):
        """
        :returns: A list of required roles (for a lokale overheid) for the user to access the view.

        Example:
        >>> ["is_beheerder", "is_redacteur"]
        """
        return []

    def test_func(self):
        role = self.request.user.roles.get(lokale_overheid=self.lokale_overheid)
        if not role:
            return False

        return all([getattr(role, r) for r in self.get_required_roles()])


class RedacteurRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures an authenticated user has "hoofdredacteur" permissions."""

    def test_func(self):
        return getattr(self.request.user, "is_hoofdredacteur")

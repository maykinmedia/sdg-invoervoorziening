from abc import ABC, abstractproperty, abstractmethod

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class OverheidRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin, ABC):
    @property
    @abstractmethod
    def allowed_roles(self):
        """
        :returns: A list of roles (for a lokale overheid) the use must have to access the view.

        For example:
        >>> ["is_beheerder", "is_redacteur"]
        """
        return []

    def test_func(self):
        role = self.request.user.roles
        role


class RedacteurRequiredMixin(LoginRequiredMixin, UserPassesTestMixin, ABC):
    """Ensure the authenticated use has global redacteur permissions."""

    def test_func(self):
        role = self.request.user.roles
        return getattr(role, "global_redacteur")

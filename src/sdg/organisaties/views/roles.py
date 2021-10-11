from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.accounts.models import Role
from sdg.organisaties.forms import LokaleOverheidForm
from sdg.organisaties.models import LokaleOverheid


class RoleListView(OverheidRoleRequiredMixin, ListView):
    template_name = "organisaties/overheid_roles.html"
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_queryset(self):
        return self.lokale_overheid.roles.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokaleoverheid"] = self.lokale_overheid
        context[
            "lokaleoverheid_beheerder"
        ] = self.lokale_overheid.user_has_manager_role(self.request.user)
        return context


# TODO: user cannot delete own role
class RoleDeleteView(OverheidRoleRequiredMixin, DeleteView):
    queryset = Role.objects.all()
    template_name = "organisaties/overheid_role_delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = ["is_beheerder"]

    def test_func(self):
        result = super().test_func()
        if not self.lokale_overheid.user_has_manager_role(self.request.user):
            return False

        return result

    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lokale_overheid=self.lokale_overheid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokaleoverheid"] = self.lokale_overheid
        return context

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:overheid_roles", kwargs={"pk": self.lokale_overheid.pk}
        )

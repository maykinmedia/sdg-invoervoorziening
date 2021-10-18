from django.core.exceptions import PermissionDenied
from django.db.models import Subquery
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.accounts.models import Role
from sdg.organisaties.views.mixins import DisallowOwnRoleMixin, RoleBaseMixin


class RoleListView(RoleBaseMixin, OverheidRoleRequiredMixin, ListView):
    template_name = "organisaties/overheid_role_list.html"
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_queryset(self):
        return self.lokale_overheid.roles.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "lokaleoverheid_beheerder"
        ] = self.lokale_overheid.user_has_manager_role(self.request.user)
        return context


class RoleDeleteView(
    DisallowOwnRoleMixin, RoleBaseMixin, OverheidRoleRequiredMixin, DeleteView
):
    queryset = Role.objects.all()
    template_name = "organisaties/overheid_role_delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = ["is_beheerder"]


class RoleUpdateView(
    DisallowOwnRoleMixin, RoleBaseMixin, OverheidRoleRequiredMixin, UpdateView
):
    queryset = Role.objects.all()
    template_name = "organisaties/overheid_role_update.html"
    pk_url_kwarg = "role_pk"
    required_roles = ["is_beheerder"]
    fields = ["is_beheerder", "is_redacteur"]

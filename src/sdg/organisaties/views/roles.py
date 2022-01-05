from django.contrib.auth import get_user_model
from django.views.generic import DeleteView, ListView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.organisaties.views.mixins import DisallowOwnRoleMixin, RoleBaseMixin

User = get_user_model()


class RoleListView(RoleBaseMixin, OverheidMixin, ListView):
    template_name = "organisaties/roles/list.html"
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_queryset(self):
        return self.lokale_overheid.roles.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "lokaleoverheid_beheerder"
        ] = self.lokale_overheid.user_has_manager_role(self.request.user)
        return context


class RoleDeleteView(DisallowOwnRoleMixin, RoleBaseMixin, OverheidMixin, DeleteView):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = ["is_beheerder"]


class RoleUpdateView(DisallowOwnRoleMixin, RoleBaseMixin, OverheidMixin, UpdateView):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/update.html"
    pk_url_kwarg = "role_pk"
    fields = ["is_beheerder", "is_redacteur"]
    required_roles = ["is_beheerder"]

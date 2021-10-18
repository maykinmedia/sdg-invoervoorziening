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


class RoleCreateView(RoleBaseMixin, OverheidRoleRequiredMixin, CreateView):
    model = Role
    template_name = "organisaties/overheid_role_create.html"
    required_roles = ["is_beheerder"]
    fields = [
        "is_beheerder",
        "is_redacteur",
        "user",
    ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        existing_qs = self.lokale_overheid.roles.all()
        form.fields["user"].queryset = form.fields["user"].queryset.exclude(
            pk__in=Subquery(existing_qs.values_list("user__pk"))
        )
        return form

    def form_valid(self, form):
        form.instance.lokale_overheid = self.lokale_overheid
        return super().form_valid(form)


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

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, ListView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.organisaties.views.mixins import DisallowOwnRoleMixin, RoleBaseMixin

User = get_user_model()


class RoleListView(RoleBaseMixin, OverheidMixin, ListView):
    template_name = "organisaties/roles/list.html"
    required_roles = [Role.choices.MANAGER, Role.choices.EDITOR]

    def get_queryset(self):
        return self.lokale_overheid.roles.all()


class RoleDeleteView(DisallowOwnRoleMixin, RoleBaseMixin, OverheidMixin, DeleteView):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = [Role.choices.MANAGER]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        name = str(self.object).split(" — ")[0]
        organisation = str(self.object).split(" — ")[-1]
        messages.success(
            self.request,
            _(
                "De gebruiker {role} is niet meer gekoppeld aan gemeente  {organisatie}."
            ).format(organisatie=organisation, role=name),
        )
        return response


class RoleUpdateView(DisallowOwnRoleMixin, RoleBaseMixin, OverheidMixin, UpdateView):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/update.html"
    pk_url_kwarg = "role_pk"
    fields = ["is_beheerder", "is_redacteur", "is_raadpleger"]
    required_roles = [Role.choices.MANAGER]

    def form_valid(self, form):
        response = super().form_valid(form)
        name = str(self.object).split(" — ")[0]
        organisation = str(self.object).split(" — ")[-1]
        messages.success(
            self.request,
            _(
                "De gebruikersrol van {role} voor gemeente {organisatie} is succesvol gewijzigd."
            ).format(organisatie=organisation, role=name),
        )
        return response

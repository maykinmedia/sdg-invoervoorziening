from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, ListView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.conf.utils import org_type_cfg
from sdg.organisaties.forms import RoleUpdateEmailForm, RoleUpdateForm
from sdg.organisaties.views.mixins import DisallowOwnRoleMixin, RoleBaseMixin

User = get_user_model()


class RoleListView(RoleBaseMixin, OverheidMixin, ListView):
    template_name = "organisaties/roles/list.html"
    required_roles = [Role.choices.MANAGER, Role.choices.EDITOR]

    def get_queryset(self):
        return self.lokale_overheid.roles.all()


class RoleDeleteView(
    DisallowOwnRoleMixin,
    RoleBaseMixin,
    OverheidMixin,
    DeleteView,
):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = [Role.choices.MANAGER]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        name = str(self.object).split(" — ")[0]
        organisation = str(self.object).split(" — ")[-1]
        cfg = org_type_cfg()

        messages.success(
            self.request,
            _(
                "De gebruiker {role} is niet meer gekoppeld aan {org_type_name} {organisatie}."
            ).format(
                org_type_name=cfg.name,
                organisatie=organisation,
                role=name,
            ),
        )
        return response


class RoleUpdateView(
    RoleBaseMixin,
    OverheidMixin,
    UpdateView,
):
    queryset = Role.objects.all()
    template_name = "organisaties/roles/update.html"
    pk_url_kwarg = "role_pk"
    form_class = RoleUpdateForm

    def get_object(self):
        try:
            return Role.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except Role.DoesNotExist:
            raise PermissionDenied()

    def get_form_class(self):
        if self.request.user == self.get_object().user:
            return RoleUpdateEmailForm

        if self.request.user.roles.get(
            lokale_overheid=self.get_object().lokale_overheid
        ).is_beheerder:
            return RoleUpdateForm

        raise PermissionDenied()

    def form_valid(self, form, *args, **kwargs):
        response = super().form_valid(form)

        name = str(self.object).split(" — ")[0]
        organisation = str(self.object).split(" — ")[-1]
        cfg = org_type_cfg()

        messages.success(
            self.request,
            _(
                "De gebruikersrol van {role} voor {org_type_name} {organisatie} is succesvol gewijzigd."
            ).format(
                org_type_name=cfg.name,
                organisatie=organisation,
                role=name,
            ),
        )
        return response

from django.core.exceptions import PermissionDenied
from django.db.models import OuterRef, Subquery
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.accounts.models import Role
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


class RoleCreateView(OverheidRoleRequiredMixin, CreateView):
    model = Role
    template_name = "organisaties/overheid_role_create.html"
    required_roles = ["is_beheerder"]
    fields = [
        "is_beheerder",
        "is_redacteur",
        "user",
    ]

    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokaleoverheid"] = self.lokale_overheid
        return context

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

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:overheid_roles", kwargs={"pk": self.lokale_overheid.pk}
        )


class RoleDeleteView(OverheidRoleRequiredMixin, DeleteView):
    queryset = Role.objects.all()
    template_name = "organisaties/overheid_role_delete.html"
    pk_url_kwarg = "role_pk"
    required_roles = ["is_beheerder"]

    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lokale_overheid=self.lokale_overheid)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.request.user.pk == self.object.user.pk:
            raise PermissionDenied()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokaleoverheid"] = self.lokale_overheid
        return context

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:overheid_roles", kwargs={"pk": self.lokale_overheid.pk}
        )

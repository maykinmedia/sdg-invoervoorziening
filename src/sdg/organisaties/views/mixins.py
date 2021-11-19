from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from sdg.organisaties.models import LokaleOverheid


class RoleBaseMixin:
    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_queryset(self):
        return self.lokale_overheid.roles.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokaleoverheid"] = self.lokale_overheid
        return context

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:roles:list", kwargs={"pk": self.lokale_overheid.pk}
        )


class DisallowOwnRoleMixin:
    def role_belongs_to_user(self) -> bool:
        return self.request.user.pk == self.object.user.pk

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.role_belongs_to_user():
            raise PermissionDenied()
        else:
            return response

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Subquery
from django.views.generic import TemplateView

from sdg.accounts.models import Role
from sdg.organisaties.models import LokaleOverheid


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context["view"].request.user

        roles = Role.objects.filter(user=user, is_redacteur=True)
        context["lokale_overheden"] = LokaleOverheid.objects.filter(
            pk__in=Subquery(roles.values("lokale_overheid")),
        )

        return context

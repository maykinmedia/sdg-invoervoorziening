from django.db.models import Q, Subquery
from django.views.generic import TemplateView

from two_factor.views import OTPRequiredMixin

from sdg.accounts.models import Role
from sdg.organisaties.models import LokaleOverheid


class HomeView(OTPRequiredMixin, TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        roles = Role.objects.filter(
            Q(is_redacteur=True) | Q(is_beheerder=True),
            user=self.request.user,
        )
        context["lokale_overheden"] = LokaleOverheid.objects.filter(
            pk__in=Subquery(roles.values("lokale_overheid")),
        )

        return context

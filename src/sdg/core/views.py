from django.db.models import Q, Subquery
from django.shortcuts import redirect
from django.views.generic import TemplateView

from sdg.accounts.mixins import VerificationMixin
from sdg.organisaties.models import LokaleOverheid


class HomeView(VerificationMixin, TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        roles = self.request.user.roles.filter(
            Q(is_redacteur=True) | Q(is_beheerder=True),
        )
        context["lokale_overheden"] = LokaleOverheid.objects.filter(
            pk__in=Subquery(roles.values("lokale_overheid")),
        )

        return context

    def get(self, request, *args, **kwargs):
        """Redirect to the municipality overview if the user has only one municipality."""
        response = super().get(request, *args, **kwargs)
        try:
            municipality = response.context_data["lokale_overheden"].get()
            return redirect(municipality.get_absolute_url())
        except (LokaleOverheid.MultipleObjectsReturned, LokaleOverheid.DoesNotExist):
            return response

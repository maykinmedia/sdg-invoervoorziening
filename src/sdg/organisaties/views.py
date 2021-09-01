from django.views.generic import DetailView, TemplateView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.organisaties.forms import LokaleOverheidForm
from sdg.organisaties.models import LokaleOverheid


class LokaleOverheidDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "organisaties/overheid_detail.html"
    model = LokaleOverheid

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie")

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class LokaleOverheidUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "organisaties/overheid_update.html"
    form_class = LokaleOverheidForm
    model = LokaleOverheid

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]

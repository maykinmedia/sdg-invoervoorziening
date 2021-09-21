from django.views.generic import CreateView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokatieDetailView(OverheidRoleRequiredMixin, CreateView):
    template_name = "organisaties/overheid_update.html"
    model = Lokatie
    get_required_roles = ["is_beheerder", "is_redacteur"]


class LokatieUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "organisaties/overheid_update.html"
    model = Lokatie
    get_required_roles = ["is_beheerder", "is_redacteur"]

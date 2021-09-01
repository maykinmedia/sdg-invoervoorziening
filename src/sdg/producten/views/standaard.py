from django.views.generic import DetailView, TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.producten.models import StandaardProductSpecifiekInformatie


class StandaardProductDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = StandaardProductSpecifiekInformatie

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


# TODO [US-02] (Lokatie)
class ContactEditView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "organisaties/overheid_update.html"

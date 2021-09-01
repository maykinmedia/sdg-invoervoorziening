from django.views.generic import DetailView, TemplateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin


class ProductDetailView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "organisaties/overheid_detail.html"


# TODO [US-02] (Lokatie)
class ContactEditView(OverheidRoleRequiredMixin, TemplateView):
    template_name = "organisaties/overheid_update.html"

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from sdg.organisaties.models import LokaleOverheid


# TODO: Delete/modify (sample view)
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lokale_overheden"] = LokaleOverheid.objects.all()
        return context

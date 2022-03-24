from django.urls import reverse_lazy
from django.views.generic import UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.organisaties.forms import LocatieInlineFormSet
from sdg.organisaties.models import LokaleOverheid


class LocatieUpdateView(OverheidMixin, UpdateView):
    template_name = "organisaties/locaties.html"
    model = LokaleOverheid
    required_roles = ["is_redacteur"]
    form_class = LocatieInlineFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, "instance": self.object, "prefix": "form"}

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:locaties", kwargs={"pk": self._lokale_overheid.pk}
        )

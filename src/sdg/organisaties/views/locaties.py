from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.core.views.mixins import SDGSettingsMixin
from sdg.organisaties.forms import LocatieInlineFormSet
from sdg.organisaties.models import LokaleOverheid


class LocatieUpdateView(
    SDGSettingsMixin,
    OverheidMixin,
    UpdateView,
):
    template_name = "organisaties/locaties.html"
    model = LokaleOverheid
    required_roles = [Role.choices.MANAGER]
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

    def form_valid(self, form):
        organisatie = self.object
        context = super().get_context_data()
        response = super().form_valid(form)
        messages.success(
            self.request,
            _(
                "De locatie instellingen van {org_type_name} {organisatie} zijn succesvol gewijzigd."
            ).format(
                org_type_name=context["org_type_cfg"].name,
                organisatie=organisatie,
            ),
        )
        return response

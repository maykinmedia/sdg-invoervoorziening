from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.conf.utils import org_type_cfg
from sdg.core.views.mixins import BreadcrumbsMixin
from sdg.organisaties.forms import BevoegdeOrganisatieInlineFormSet
from sdg.organisaties.models import LokaleOverheid


class BevoegdeOrganisatieUpdateView(
    BreadcrumbsMixin,
    OverheidMixin,
    UpdateView,
):
    template_name = "organisaties/bevoegde_organisaties.html"
    model = LokaleOverheid
    required_roles = [Role.choices.MANAGER]
    form_class = BevoegdeOrganisatieInlineFormSet
    breadcrumbs_title = _("Bevoegde organisaties")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, "instance": self.object, "prefix": "form"}

    def get_lokale_overheid(self):
        self.object = self.lokale_overheid = self.get_object()
        return self.lokale_overheid

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:bevoegde_organisaties",
            kwargs={"pk": self._lokale_overheid.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _(
                "De bevoegde organisaties van {org_type_name} {organisatie} zijn succesvol gewijzigd."
            ).format(
                org_type_name=org_type_cfg().name,
                organisatie=self.lokale_overheid,
            ),
        )
        return response

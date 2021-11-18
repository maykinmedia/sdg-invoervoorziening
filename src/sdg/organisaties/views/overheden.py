from copy import deepcopy

from django.db.models import Case, Q, Subquery, When
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.models import Thema
from sdg.organisaties.forms import LokaleOverheidForm, LokatieInlineFormSet
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product


class LokaleOverheidUpdateView(OverheidMixin, UpdateView):
    template_name = "organisaties/update.html"
    form_class = LokaleOverheidForm
    model = LokaleOverheid
    required_roles = ["is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["formset"] = kwargs.get("formset") or LokatieInlineFormSet(
            instance=self.object, prefix="form"
        )
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.object)
        formset = LokatieInlineFormSet(
            request.POST, instance=self.object, prefix="form"
        )

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset=formset)
        else:
            return self.form_invalid(form, formset=formset)

    def form_valid(self, form, formset=None):
        self.object = form.save()
        if formset:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset=None):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

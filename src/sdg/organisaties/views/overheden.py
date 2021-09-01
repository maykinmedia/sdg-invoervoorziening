from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.organisaties.forms import (
    LokaleOverheidForm,
    LokatieForm,
    LokatieFormHelper,
    LokatieInlineFormSet,
)
from sdg.organisaties.models import LokaleOverheid


class LokaleOverheidDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "organisaties/overheid_detail.html"
    model = LokaleOverheid

    def get_context_data(self, **kwargs):
        return super().get_context_data()
        # TODO: Get products (all from catalog 1)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["formset"] = LokatieInlineFormSet(instance=self.object)
        context["lokatie_helper"] = LokatieFormHelper()

        return context

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        form = self.form_class(request.POST, instance=self.object)
        formset = LokatieInlineFormSet(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset=formset)
        else:
            form_errors = [] if not form.errors else form.errors
            formset_errors = [] if not formset.errors else formset.errors
            for obj in [*form_errors, *formset_errors]:
                for field, error in obj.items():
                    messages.error(request, f"{field}: {error.as_text()}")
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

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]

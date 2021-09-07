from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.organisaties.forms import (
    LokaleOverheidForm,
    LokatieFormHelper,
    LokatieInlineFormSet,
)
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import StandaardProductSpecifiekInformatie


class LokaleOverheidDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "organisaties/overheid_detail.html"
    model = LokaleOverheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context[
            "standaardproducten"
        ] = StandaardProductSpecifiekInformatie.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            "lokaties",
            "organisatie",
            "catalogi",
            "catalogi__producten",
        )

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class LokaleOverheidUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "organisaties/overheid_update.html"
    form_class = LokaleOverheidForm
    model = LokaleOverheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["lokatie_formset"] = kwargs.get("formset") or LokatieInlineFormSet(
            instance=self.object, prefix="form"
        )
        context["lokatie_helper"] = LokatieFormHelper()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

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

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]

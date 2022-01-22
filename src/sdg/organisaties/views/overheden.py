from django.http import HttpResponseRedirect
from django.views.generic import UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.types import Event
from sdg.organisaties.forms import LocatieInlineFormSet, LokaleOverheidForm
from sdg.organisaties.models import LokaleOverheid


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

        context["formset"] = kwargs.get("formset") or LocatieInlineFormSet(
            instance=self.object, prefix="form"
        )
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.object)
        formset = LocatieInlineFormSet(
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
        Event.create_and_log(self.request, self.object, Event.UPDATE)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset=None):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

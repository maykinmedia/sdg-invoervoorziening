from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView, FormView, UpdateView

from sdg.accounts.mixins import RootEditorRequiredMixin
from sdg.producten.forms import GegevensFormHelper, ProductReferentieInformatieFormset
from sdg.producten.models import ReferentieProduct


class ReferentieProductDetailView(RootEditorRequiredMixin, DetailView):
    template_name = "producten/product_detail.html"
    model = ReferentieProduct
    queryset = ReferentieProduct.objects.prefetch_related(
        "informatie",
    ).all()

    @staticmethod
    def get_required_roles():
        return ["is_beheerder", "is_redacteur"]


class ReferentieProductUpdateView(RootEditorRequiredMixin, UpdateView):
    template_name = "producten/product_edit.html"

    model = ReferentieProduct
    form_class = ProductReferentieInformatieFormset

    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_helper"] = GegevensFormHelper()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

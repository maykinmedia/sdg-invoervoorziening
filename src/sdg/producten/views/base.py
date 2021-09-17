from django.http import HttpResponseRedirect
from django.views.generic import UpdateView

from .mixins import ProductFormSetMixin


class BaseProductUpdateView(ProductFormSetMixin, UpdateView):
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

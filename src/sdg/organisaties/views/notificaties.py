from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from sdg.producten.models import ProductVersie


class ProductVersieListView(LoginRequiredMixin, ListView):
    model = ProductVersie
    template_name = "organisaties/notificaties/list.html"
    context_object_name = "versions"
    limit = 25

    def get_queryset(self):
        """
        Returns the queryset for the notifications (product versions).
        """
        return ProductVersie.objects.published().order_by("-gewijzigd_op")[: self.limit]

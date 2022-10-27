from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.views.generic import ListView

from dateutil.relativedelta import relativedelta

from sdg.producten.models import ProductVersie


class ProductVersieListView(LoginRequiredMixin, ListView):
    """
    Product version list view. Referred to as "notifications".

    limit: The maximum number of notifications to show.
    max_months_old: The maximum age of notifications to show.
    """

    model = ProductVersie
    template_name = "organisaties/notificaties/list.html"
    context_object_name = "versions"
    limit = 25
    max_months_old = 12

    def get_queryset(self):
        """
        Returns the queryset for the notifications (product versions).
        """
        x_months_ago = now() - relativedelta(months=self.max_months_old)
        return (
            ProductVersie.objects.filter(
                product__referentie_product=None,
                gewijzigd_op__gte=x_months_ago,
            )
            .published()
            .order_by("-gewijzigd_op")[: self.limit]
        )

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.generic import ListView

from dateutil.relativedelta import relativedelta

from sdg.core.views.mixins import BreadcrumbsMixin
from sdg.producten.models import NotificationViewed, ProductVersie


class ProductVersieListView(
    BreadcrumbsMixin,
    LoginRequiredMixin,
    ListView,
):
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
    breadcrumbs_title = _("Notificaties")

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

    def get(self, request, *args, **kwargs):
        # Call the parent class's get method to fetch the queryset
        response = super().get(request, *args, **kwargs)

        # Get or create the NotificationViewed instance for the current user
        notification_viewed, create = NotificationViewed.objects.get_or_create(
            gebruiker=request.user
        )

        # Update the last_viewed_date to the current time
        notification_viewed.last_viewed_date = timezone.now()
        notification_viewed.save()

        return response

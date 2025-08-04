from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.generic import ListView

from dateutil.relativedelta import relativedelta

from sdg.accounts.mixins import OverheidMixin
from sdg.core.views.mixins import BreadcrumbsMixin
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import NotificationViewed, ProductVersie


class ProductVersieListView(
    OverheidMixin,
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

    def get_lokale_overheid(self):
        """
        Returns the LokaleOverheid object for local municipality.
        """
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])

        return self.lokale_overheid

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

        # Raise permission denied error if the notification page
        # of a different lokale_overheid is requested.
        valid_request = any(
            [
                kwargs["pk"] == str(role.lokale_overheid.pk)
                for role in request.user.roles.all()
            ]
        )

        if not valid_request:
            raise PermissionDenied()

        # Update or create the NotificationViewed instance for the current user
        NotificationViewed.objects.update_or_create(gebruiker=request.user)

        return response

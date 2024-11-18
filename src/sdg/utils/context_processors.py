from django.conf import settings as django_settings
from django.utils.timezone import now

from dateutil.relativedelta import relativedelta

from sdg.conf.utils import org_type_cfg
from sdg.producten.models import NotificationViewed, ProductVersie


def settings(request):
    public_settings = (
        "GOOGLE_ANALYTICS_ID",
        "ENVIRONMENT",
        "SHOW_ALERT",
        "PROJECT_NAME",
        "RELEASE",
        "SUBPATH",
        "SDG_CMS_PRODUCTS_DISABLED",
    )

    context = {
        "settings": dict(
            [(k, getattr(django_settings, k, None)) for k in public_settings]
        ),
        "org_type_cfg": org_type_cfg(),
    }

    if hasattr(django_settings, "SENTRY_CONFIG"):
        context.update(dsn=django_settings.SENTRY_CONFIG.get("public_dsn", ""))

    return context


def has_new_notifications(request):
    user = request.user
    has_new_notifications = False

    if user and user.is_anonymous is not True:
        try:
            notification_viewed = NotificationViewed.objects.get(gebruiker=user)
            last_viewed_date = notification_viewed.last_viewed_date
        except NotificationViewed.DoesNotExist:
            notification_viewed = None
            # By default, the last_viewed_date is set to 12 months ago.
            last_viewed_date = now() - relativedelta(months=12)

        # Get the latest product versie (notifications are based on ProductVersie) later than last_viewed_date.
        latest_notification = (
            ProductVersie.objects.select_related("product")
            .filter(
                product__referentie_product=None,
                gewijzigd_op__gt=last_viewed_date,
            )
            .order_by("-gewijzigd_op")
            .first()
        )

        has_new_notifications = bool(latest_notification)

    return {
        "has_new_notifications": has_new_notifications,
    }

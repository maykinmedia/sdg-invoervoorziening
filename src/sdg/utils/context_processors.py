from django.conf import settings as django_settings

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
    if request.user and request.user.is_anonymous != True:
        # Get the user's NotificationViewed instance
        notification_viewed = NotificationViewed.objects.get(gebruiker=request.user)

        # Get the latest product version after the last_viewed_date else None.
        latest_notification = (
            ProductVersie.objects.filter(
                product__referentie_product=None,
                gewijzigd_op__gt=notification_viewed.last_viewed_date,
            )
            .order_by("-gewijzigd_op")
            .first()
        )

        # Check if there is a new notification
        has_new = latest_notification is not None

        return {
            "has_new_notifications": has_new,
            "latest_notification_date": (
                latest_notification.gewijzigd_op if latest_notification else None
            ),
        }

    return {
        "has_new_notifications": False,
        "latest_notification_date": None,
    }

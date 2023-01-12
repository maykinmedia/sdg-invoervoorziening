from django.conf import settings as django_settings

from sdg.conf.utils import org_type_cfg


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

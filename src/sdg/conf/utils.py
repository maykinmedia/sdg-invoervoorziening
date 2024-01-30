import logging
from functools import lru_cache

from django.conf import settings

from decouple import Csv, config as _config, undefined
from sentry_sdk.integrations import DidNotEnable, django, redis

from sdg.conf.types.organization import OrganizationTypeConfiguration

logger = logging.getLogger(__name__)


def config(option: str, default=undefined, *args, **kwargs):
    """
    Pull a config parameter from the environment.

    Read the config variable ``option``. If it's optional, use the ``default`` value.
    Input is automatically cast to the correct type, where the type is derived from the
    default value if possible.

    Pass ``split=True`` to split the comma-separated input into a list.
    """
    transform = kwargs.pop("transform", lambda x: x)

    if "split" in kwargs:
        kwargs.pop("split")
        kwargs["cast"] = Csv()

    if default is not undefined and default is not None:
        kwargs.setdefault("cast", type(default))

    return transform(_config(option, default=default, *args, **kwargs))


def get_sentry_integrations() -> list:
    """
    Determine which Sentry SDK integrations to enable.
    """
    default = [
        django.DjangoIntegration(),
        redis.RedisIntegration(),
    ]
    extra = []

    try:
        from sentry_sdk.integrations import celery
    except DidNotEnable:  # happens if the celery import fails by the integration
        pass
    else:
        extra.append(celery.CeleryIntegration())

    return [*default, *extra]


@lru_cache
def org_type_cfg():
    """
    Get the organization type configuration for the current environment.
    """
    from sdg.conf.types.organization import available_org_types

    return OrganizationTypeConfiguration(
        **available_org_types[settings.SDG_ORGANIZATION_TYPE]
    )

import codecs
import logging
import os
import re
from shutil import which
from subprocess import CalledProcessError, check_output

from django.conf import settings

import pydantic
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


def _get_version_from_file():
    """
    Returns a commit hash from the project's .git/ dir if it exists
    """
    heads_dir = os.path.join(settings.BASE_DIR, ".git", "refs", "heads")

    try:
        heads = os.listdir(heads_dir)
    except FileNotFoundError:
        logging.warning("Unable to read commit hash from git files")
        return ""

    for filename in ("master", "main", "develop"):
        if filename in heads:
            try:
                with open(os.path.join(heads_dir, filename)) as file:
                    return file.read().strip()
            except OSError:
                logging.warning("Unable to read commit hash from file")

    return ""


def _get_version_from_git():
    """
    Returns the current tag or commit hash supplied by git
    """
    try:
        tags = check_output(
            ["git", "tag", "--points-at", "HEAD"], universal_newlines=True
        )
    except CalledProcessError:
        logger.warning("Unable to list tags")
        tags = None

    if tags:
        return next(version for version in tags.splitlines())

    try:
        commit = check_output(["git", "rev-parse", "HEAD"], universal_newlines=True)
    except CalledProcessError:
        logger.warning("Unable to list current commit hash")
        commit = None

    return commit or ""


def get_current_version():
    version = config("VERSION_TAG", default=None)

    if version:
        return version
    elif which("git"):
        return _get_version_from_git()

    return _get_version_from_file()


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, "r", "utf8") as f:
        return f.read()


def clean_rst(text: str) -> str:
    """Clean up unneeded rst characters."""
    text = re.sub(r"((?P<title>.*)\n={2,})", r"# \g<title>", text)
    text = re.sub(r"[|:][\w-]+[|:]", "", text)
    text = re.sub(r"(.)\1{4,}", "", text)
    return text


@pydantic.tools.lru_cache
def org_type_cfg():
    """
    Get the organization type configuration for the current environment.
    """
    from sdg.conf.types.organization import available_org_types

    return OrganizationTypeConfiguration(
        **available_org_types[getattr(settings, "SDG_ORGANIZATION_TYPE")]
    )

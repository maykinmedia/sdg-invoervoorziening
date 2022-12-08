from django.conf import settings
from django.db import transaction

from sdg.celery import app
from sdg.core.constants.logius import PublicData
from sdg.core.types import LoadCommand

if settings.SDG_ORGANIZATION_TYPE == "municipality":
    organization = PublicData.MUNICIPALITY
elif settings.SDG_ORGANIZATION_TYPE == "province":
    organization = PublicData.PROVINCE
elif settings.SDG_ORGANIZATION_TYPE == "waterauthority":
    organization = PublicData.WATERAUTHORITY
else:
    organization = None


management_commands = [
    LoadCommand("load_government_orgs", PublicData.GOVERNMENT_ORGANISATION),
    LoadCommand("load_organisation_subset", organization),
    LoadCommand("load_informatiegebieden", PublicData.INFORMATIEGEBIED),
    LoadCommand("load_upn", PublicData.UPN),
]


@app.task()
def import_logius_data():
    """Import logius data using external public sources."""

    with transaction.atomic():
        for command in management_commands:
            command.execute()

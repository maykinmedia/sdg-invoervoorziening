from django.conf import settings
from django.db import transaction

from sdg.celery import app
from sdg.core.constants.logius import PublicData
from sdg.core.types import LoadCommand

management_commands = [
    LoadCommand("load_government_orgs", PublicData.GOVERNMENT_ORGANISATION),
    LoadCommand("load_informatiegebieden", PublicData.INFORMATIEGEBIED),
    LoadCommand("load_upn", PublicData.UPN),
]

if settings.SDG_ORGANIZATION_TYPE == "municipalities":
    management_commands += [LoadCommand("load_municipalities", PublicData.MUNICIPALITY)]
elif settings.SDG_ORGANIZATION_TYPE == "provinces":
    management_commands += [LoadCommand("load_municipalities", PublicData.PROVINCE)]


@app.task()
def import_logius_data():
    """Import logius data using external public sources."""

    with transaction.atomic():
        for command in management_commands:
            command.execute()

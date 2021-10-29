from django.db import transaction

from sdg.conf import celery_app
from sdg.core.constants.logius import PublicData
from sdg.core.types import LoadCommand

management_commands = [
    LoadCommand("load_gemeenten", PublicData.GEMEENTE),
    LoadCommand("load_upn", PublicData.UPN),
    LoadCommand("load_informatiegebieden", PublicData.INFORMATIEGEBIED),
    LoadCommand("load_upn_informatiegebieden", PublicData.UPN_INFORMATIEGEBIED),
]


@celery_app.task()
def import_logius_data():
    """Import logius data using external public sources."""

    with transaction.atomic():
        for command in management_commands:
            command.execute()

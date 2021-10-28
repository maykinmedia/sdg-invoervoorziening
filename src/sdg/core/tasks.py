from django.core.management import call_command
from django.db import transaction

from sdg.conf import celery_app
from sdg.core.constants.logius import PublicData


@celery_app.task()
def import_logius_data():
    """Import logius data using external public sources."""

    with transaction.atomic():
        call_command("load_gemeenten", PublicData.GEMEENTE)
        call_command("load_upn", PublicData.UPN)
        call_command("load_informatiegebieden", PublicData.INFORMATIEGEBIED)
        call_command("load_upn_informatiegebieden", PublicData.UPN_INFORMATIEGEBIED)

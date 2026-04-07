import io

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from sdg.celery import app
from sdg.core.constants.logius import PublicData
from sdg.core.export import ApplicationExporter
from sdg.core.models import ApplicationRapport
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


@app.task()
def create_application_export(application_export_pk: str):
    export_model = ApplicationRapport.objects.get(pk=application_export_pk)

    with io.BytesIO() as export_file:
        datetime = export_model.gemaakt_op.strftime("%Y-%m-%dT%H-%M-%S")
        name = f"application_rapport_{datetime}.xlsx"
        ApplicationExporter(export_file)

        export_model.file = File(file=export_file, name=name)
        export_model.save()


@app.task()
def clean_application_exports(days: int = 30):
    """
    Remove all rapports that were created over X days ago.
    The default is set to 30 days.
    """

    remove_before = timezone.now().date() - timezone.timedelta(days=int(days))
    ApplicationRapport.objects.filter(gemaakt_op__lt=remove_before).delete()

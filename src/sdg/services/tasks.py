from django.core.management import call_command

from sdg.celery import app


@app.task()
def import_data_from_services():
    call_command("import_data_from_services")

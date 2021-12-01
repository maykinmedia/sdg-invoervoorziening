from django.core.management import call_command

from sdg.celery import app


@app.task()
def autofill():
    """Automatically create generic and reference products."""
    call_command("autofill")

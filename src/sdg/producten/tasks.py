from django.core.management import call_command

from sdg.celery import app


@app.task()
def autofill():
    """Automatically create generic and reference products."""
    call_command("autofill")


@app.task()
def update_catalogs():
    """
    Create, update, correct all specific products for each organisation.
    """
    call_command("update_catalogs")


@app.task()
def update_generic_product_status():
    """
    Create, update, correct all specific products for each organisation.
    """
    call_command("update_generic_product_status")

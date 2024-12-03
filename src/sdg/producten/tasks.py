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
    Generate and update the status of all generic products.
    """
    call_command("update_generic_product_status")


@app.task()
def check_broken_links():
    """
    Create, update and remove broken links from the database.
    """
    call_command("check_broken_links")


@app.task()
def send_monthly_broken_links_report():
    """
    Send monthly broken links report to the all redactors of the content.
    """
    call_command("send_monthly_broken_links_report")

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


@app.task(
    time_limit=60 * 60 * 12,  # 12 hours
    soft_time_limit=60 * 60 * 11,  # 11 hours
)
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


@app.task()
def automatisch_doordrukken_teksten():
    """
    Generate and update the status of all generic products.
    """
    call_command("automatisch_doordrukken_teksten")


@app.task()
def send_email_to_users_about_doordrukken():
    """
    Send an e-mail to users to inform them about their product and that a reference product will overwrite it.
    """
    call_command("send_email_to_users_about_doordrukken")

import datetime

from django.conf import settings
from django.core.management import call_command

from sdg.celery import app
from sdg.core.models.config import SiteConfiguration


@app.task()
def send_notifications():
    """Automatically sends notification emails."""

    last_send = SiteConfiguration.objects.first().mail_text_changes_last_sent
    send_every_x_days = datetime.timedelta(
        days=settings.SDG_MAIL_TEXT_CHANGES_EVERY_DAYS
    )

    if (last_send + send_every_x_days) <= datetime.date.today():
        call_command("send_notification_mail")

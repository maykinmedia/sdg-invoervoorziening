import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils.html import strip_tags
from django.utils.timezone import now

from compat import render_to_string
from dateutil.relativedelta import relativedelta

from sdg.accounts.models import User
from sdg.core.models.config import SiteConfiguration
from sdg.producten.models.product import ProductVersie


class Command(BaseCommand):
    help = f"Send product update notification emails from last ({settings.SDG_MAIL_TEXT_CHANGES_EVERY_DAYS}) days to subscribed users."

    def handle(self, **options):
        x_days_ago = now() - relativedelta(
            days=settings.SDG_MAIL_TEXT_CHANGES_EVERY_DAYS
        )
        product_versies = (
            ProductVersie.objects.filter(
                product__referentie_product=None,
                gewijzigd_op__gte=x_days_ago,
            )
            .published()
            .order_by("-gewijzigd_op")
        )
        if product_versies:

            users = (
                User.objects.filter(roles__ontvangt_mail=True)
                .order_by("email")
                .distinct("email")
            )

            for user in users:
                mail_ctx = {
                    "user_full_name": user.get_full_name(),
                    "product_versions": product_versies,
                }

                html_message = render_to_string(
                    "organisaties/notificaties/email/notificatie.html", context=mail_ctx
                )

                send_mail(
                    "Aanpassing in tekst SDG-invoervoorziening",
                    strip_tags(html_message),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully send emails to {len(users)} user(s)")
            )

        config = SiteConfiguration.objects.first()
        config.mail_text_changes_last_sent = datetime.date.today()
        config.save()

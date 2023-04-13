import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.timezone import now

from compat import render_to_string
from dateutil.relativedelta import relativedelta

from sdg.accounts.models import User
from sdg.conf.utils import org_type_cfg
from sdg.core.models.config import SiteConfiguration
from sdg.producten.models.product import ProductVersie


class Command(BaseCommand):
    help = f"Send product update notification emails from last ({settings.SDG_MAIL_TEXT_CHANGES_EVERY_DAYS}) days to subscribed users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            metavar=["email", "username"],
            help="Send to email to one specific user instead based on 'email' or 'username'.",
        )

    def get_user_by_email(self, user):
        return (
            User.objects.filter(email=user, roles__ontvangt_mail=True)
            .order_by("email")
            .distinct("email")
        )

    def get_user_by_username(self, user):
        user_qs = (
            User.objects.filter(roles__ontvangt_mail=True)
            .order_by("email")
            .distinct("email")
        )
        if user_qs:
            for search_term in user.split():
                user_qs = user_qs.filter(
                    Q(first_name__iexact=search_term) | Q(last_name__iexact=search_term)
                )
        return user_qs

    def handle(self, user, **options):
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
            if user:
                user_qs = self.get_user_by_email(user)
                if not user_qs:
                    user_qs = self.get_user_by_username(user)
            else:
                user_qs = (
                    User.objects.filter(roles__ontvangt_mail=True)
                    .order_by("email")
                    .distinct("email")
                )

            if user_qs:
                organisation_name = org_type_cfg().organisation_name

                for user in user_qs:
                    mail_ctx = {
                        "user_full_name": user.get_full_name(),
                        "product_versions": product_versies,
                        "org_name": organisation_name,
                    }

                    html_message = render_to_string(
                        "organisaties/notificaties/email/notificatie.html",
                        context=mail_ctx,
                    )

                    send_mail(
                        "Aanpassing in tekst SDG-invoervoorziening",
                        strip_tags(html_message),
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully send emails to {len(user_qs)} user(s)"
                    )
                )

        config = SiteConfiguration.get_solo()
        config.mail_text_changes_last_sent = datetime.date.today()
        config.save()

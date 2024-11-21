from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags

from compat import render_to_string
from furl import furl

from sdg.conf.utils import org_type_cfg
from sdg.producten.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = "Send an e-mail to users to inform them about their related products and that they will be overwritten."

    def send_mail(self, user, product_url):
        mail_context = {
            "user_full_name": user.get_full_name(),
            "sender_organization": org_type_cfg().organisation_name,
            "product_url": product_url,
        }

        html_message = render_to_string(
            "producten/email/email_inform_about_doordrukken.html",
            context=mail_context,
        )

        print(html_message)

        send_mail(
            "30 dagen tot een product in SDG automatisch zal worden gepubliceerd.",
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )

    def handle(self, *args, **options):
        doordruk_datum = date.today() + timedelta(days=30)

        for product in Product.objects.filter(
            referentie_product__isnull=False,
            automatisch_doordrukken=True,
            automatisch_doordrukken_datum=doordruk_datum,
        ):
            lokale_overheid = product.catalogus.lokale_overheid

            url_scheme = "https" if settings.IS_HTTPS else "http"
            url_netloc = Site.objects.get_current().domain.rstrip("/")
            url_path_to_product = reverse(
                "organisaties:catalogi:producten:edit",
                kwargs={
                    "pk": lokale_overheid.pk,
                    "catalog_pk": product.catalogus.pk,
                    "product_pk": product.pk,
                },
            ).lstrip("/")
            url_path_list = [
                segment
                for segment in [settings.SUBPATH, url_path_to_product]
                if segment
            ]
            product_url = furl(scheme=url_scheme, netloc=url_netloc, path=url_path_list)
            product_url.args["doordrukken_action_taken"] = True

            receiver_roles = lokale_overheid.roles.filter(
                Q(is_redacteur=True, ontvangt_mail=True)
            )

            if len(receiver_roles) == 0:
                receiver_roles = lokale_overheid.roles.filter(
                    Q(is_beheerder=True, ontvangt_mail=True)
                )

            for role in receiver_roles:
                self.send_mail(role.user, product_url=product_url.url)

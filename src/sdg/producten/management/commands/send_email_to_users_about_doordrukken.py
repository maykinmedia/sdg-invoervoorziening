from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.urls import reverse
from django.utils.html import strip_tags

from compat import render_to_string
from furl import furl

from sdg.accounts.models import Role
from sdg.conf.utils import org_type_cfg
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = "Send an e-mail to users to inform them about their related products and that they will be overwritten."

    def construct_product_url(
        self,
        lokale_overheid: LokaleOverheid,
        catalogus: ProductenCatalogus,
        product: Product,
    ) -> furl:
        url_scheme = "https" if settings.IS_HTTPS else "http"
        url_netloc = Site.objects.get_current().domain.rstrip("/")
        url_partial_path = reverse(
            "organisaties:catalogi:producten:edit",
            kwargs={
                "pk": lokale_overheid.pk,
                "catalog_pk": catalogus.pk,
                "product_pk": product.pk,
            },
        ).lstrip("/")

        url_path = [
            segment for segment in [settings.SUBPATH, url_partial_path] if segment
        ]

        return furl(
            scheme=url_scheme,
            netloc=url_netloc,
            path=url_path,
        )

    def create_and_send_mail(
        self,
        user,
        product: Product,
        catalogus: ProductenCatalogus,
        lokale_overheid: LokaleOverheid,
    ):
        cfg = org_type_cfg()
        product_url = self.construct_product_url(lokale_overheid, catalogus, product)
        mail_context = {
            "user_full_name": user.get_full_name(),
            "sender_organization": cfg.organisation_name,
            "product": product,
            "product_url": product_url.url,
            "product_url_with_action_query": product_url.add(
                args={"doordrukken_action_taken": True}
            ).url,
            "org_type_name": cfg.name,
            "lokale_overheid": lokale_overheid,
            "doordruk_date": settings.SDG_PRESS_THROUGH_DAYS,
        }

        html_message = render_to_string(
            "producten/email/email_inform_about_doordrukken.html",
            context=mail_context,
        )

        send_mail(
            f"{settings.SDG_PRESS_THROUGH_DAYS} dagen tot een SDG-producttekst automatisch wordt gepubliceerd",
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )

    def handle(self, *args, **options):
        # Get all specific products that will be pressed through in 30 days from now (not reference products).
        for product in Product.objects.filter(
            referentie_product__isnull=False,
            automatisch_doordrukken=True,
            automatisch_doordrukken_datum=date.today()
            + timedelta(days=settings.SDG_PRESS_THROUGH_DAYS),
        ):
            catalogus: ProductenCatalogus = product.catalogus
            lokale_overheid: LokaleOverheid = catalogus.lokale_overheid
            roles: BaseManager[Role] = lokale_overheid.roles

            receiver_roles = (
                # Receivers are every redactor with mailing on if there are redactors.
                roles.filter(Q(is_redacteur=True, ontvangt_mail=True))
                if roles.filter(Q(is_redacteur=True, ontvangt_mail=True)).count() >= 1
                # When there are no redactors as receivers, send the e-mail to every admin with mailing on.
                else roles.filter(Q(is_beheerder=True, ontvangt_mail=True))
            )

            for role in receiver_roles:
                self.create_and_send_mail(
                    role.user, product, catalogus, lokale_overheid
                )

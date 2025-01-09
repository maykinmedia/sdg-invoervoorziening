from collections import defaultdict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.html import strip_tags

from compat import render_to_string
from furl import furl

from sdg.accounts.models import Role
from sdg.conf.utils import org_type_cfg
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import BrokenLinks

User = get_user_model()


class Command(BaseCommand):
    help = "Send monthly broken links report to the all redactors of the content."

    def construct_base_url(
        self,
    ) -> furl:
        url_scheme = "https" if settings.IS_HTTPS else "http"
        url_netloc = Site.objects.get_current().domain.rstrip("/")
        url_path = [segment for segment in [settings.SUBPATH] if segment]

        return furl(
            scheme=url_scheme,
            netloc=url_netloc,
            path=url_path,
        )

    def create_and_send_mail(
        self, user, broken_links, multiple_organizations: bool, user_organizations
    ):
        def sort_compare_fn(broken_link):
            return (
                broken_link.product.catalogus.lokale_overheid.__str__(),
                broken_link.product.name,
                broken_link.occurring_field,
            )

        org_type_name = org_type_cfg().name

        mail_context = {
            "user_full_name": user.get_full_name(),
            "broken_links": sorted(broken_links, key=sort_compare_fn),
            "sender_organization": org_type_cfg().organisation_name,
            "org_type_name": org_type_name,
            "multiple_organizations": multiple_organizations,
            "base_url": self.construct_base_url(),
            "user_organizations": user_organizations,
        }

        html_message = render_to_string(
            "producten/email/email_broken_links.html",
            context=mail_context,
        )

        send_mail(
            f"Foute links in SDG-{org_type_name.lower()}teksten",
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )

    def handle(self, *args, **options):
        """
        Description:
        ------------
        Send an email with a report of the broken links to all roles with `ontvangt_mail = True` and `is_redacteur = True`. In case a lokale_overheid has only the roles
        `is_beheerder = True` and `is_redacteur = False` send the e-mail to the admins.
        """

        grouped_users = defaultdict(lambda: ([], set(), None))

        # First create mailing list
        for broken_link in BrokenLinks.objects.filter(error_count__gte=3):
            lokale_overheid: LokaleOverheid = (
                broken_link.product.catalogus.lokale_overheid
            )
            organization_id = lokale_overheid.organisatie_id
            roles: Role = lokale_overheid.roles

            receiver_roles: Role = (
                # Receivers are every redactor with mailing on if there are redactors.
                roles.filter(Q(is_redacteur=True, ontvangt_mail=True))
                if roles.filter(Q(is_redacteur=True, ontvangt_mail=True)).count() >= 1
                # When there are no redactors as receivers, send the e-mail to every admin with mailing on.
                else roles.filter(Q(is_beheerder=True, ontvangt_mail=True))
            )

            for receiver_role in receiver_roles:
                broken_links, user_organizations, user = grouped_users[
                    receiver_role.user.email
                ]
                user_organizations.add(lokale_overheid.organisatie)
                broken_links.append(broken_link)
                # Update user
                grouped_users[receiver_role.user.email] = (
                    broken_links,
                    user_organizations,
                    receiver_role.user,
                )

        # Send a mail to each user
        for broken_links, user_organizations, user in grouped_users.values():
            multiple_organizations = len(user_organizations) > 1
            self.create_and_send_mail(
                user=user,
                broken_links=broken_links,
                multiple_organizations=multiple_organizations,
                user_organizations=user_organizations,
            )

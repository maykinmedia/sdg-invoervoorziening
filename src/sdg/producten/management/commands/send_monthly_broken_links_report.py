from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.html import strip_tags

from compat import render_to_string

from sdg.conf.utils import org_type_cfg
from sdg.producten.models import BrokenLinks

User = get_user_model()


class BaseMail:
    """
    Description:
    ------------
    Abstract base mail implementation build for the send monthly broken links command.
    This class is used to handle the email (create and send).

    Parameters:
    -----------
    - user : User
    - organization_id : int
    - broken_link : BrokenLinks
    """

    def __init__(self, user, organization_id, broken_link, **kwargs):
        self.user_full_name = user.get_full_name()
        self.organizations = {organization_id}
        self.broken_links = [broken_link]
        self.receiver = user.email
        self.sender_organization = org_type_cfg().organisation_name
        self.ALLOW_MAILING = kwargs.get("allow_mailing", True)

    def append_broken_link(self, broken_link, organization_id):
        self.organizations.add(organization_id)
        self.broken_links.append(broken_link)

    def send_mail(self):
        html_message = self.__create_email()
        if self.ALLOW_MAILING:
            send_mail(
                "Rapportage foutieve links in SDG-invoervoorziening",
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [self.receiver],
                html_message=html_message,
            )

    def __create_email(self):
        mail_context = {
            "user_full_name": self.user_full_name,
            "broken_links": self.broken_links,
            "sender_organization": self.sender_organization,
            "multiple_organizations": len(self.organizations) > 1,
        }

        return render_to_string(
            "producten/email/email_broken_links.html",
            context=mail_context,
        )


class Command(BaseCommand):
    help = "Send monthly broken links report to the all redactors of the content."

    def create_or_append_receiver(
        self,
        user,
        organisatie_id: str,
        broken_link: BrokenLinks,
        data: dict[str, BaseMail],
    ):
        base_mail = data.get(user.email)
        if base_mail is not None:
            base_mail.append_broken_link(
                broken_link=broken_link, organization_id=organisatie_id
            )
        else:
            data[user.email] = BaseMail(
                allow_mailing=False,
                user=user,
                organization_id=organisatie_id,
                broken_link=broken_link,
            )

    def handle(self, *args, **options):
        """
        Description:
        ------------
        Send an email with a report of the broken links to all roles with `ontvangt_mail = True` and `is_redacteur = True`. In case a lokale_overheid has only the roles
        `is_beheerder = True` and `is_redacteur = False` send the e-mail to the admins.
        """
        mailing_dict: dict[str, BaseMail] = {}
        notified_broken_links = BrokenLinks.objects.filter(error_count__gte=3)
        self.stdout.write(
            self.style.SUCCESS(
                f"There is a total of {len(notified_broken_links)} broken_links."
            )
        )

        # First create mailing list
        for broken_link in notified_broken_links:
            roles = broken_link.product.catalogus.lokale_overheid.roles
            organization_id = (
                broken_link.product.catalogus.lokale_overheid.organisatie.id
            )

            # Receiver (every redactor with ontvangt_email=True)
            receiver_roles = roles.filter(Q(is_redacteur=True, ontvangt_mail=True))

            if len(receiver_roles) == 0:
                # Receiver (every admin with ontvangt_email=True)
                receiver_roles = roles.filter(Q(is_beheerder=True, ontvangt_mail=True))

            for receiver_role in receiver_roles:
                user = receiver_role.user
                base_mail = mailing_dict.get(receiver_role.user.email)
                if base_mail is not None:
                    base_mail.append_broken_link(
                        broken_link=broken_link, organization_id=organization_id
                    )
                else:
                    mailing_dict[receiver_role.user.email] = BaseMail(
                        allow_mailing=False,
                        user=user,
                        organization_id=organization_id,
                        broken_link=broken_link,
                    )

        # Then send out emails
        try:
            for base_mail in mailing_dict.values():
                base_mail.send_mail()
        finally:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully send emails to {len(mailing_dict.values())} user(s)"
                )
            )

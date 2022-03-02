from django.utils.translation import ugettext_lazy as _

from sdg.core.events import CustomMessageEvent


class InviteUser(CustomMessageEvent):
    """Send an invitation to a user, setting the inviter as the request user."""

    default_message = _(
        "Het account kon niet worden aangemaakt omdat de e-mail service niet beschikbaar is."
    )
    admin_message = _(
        "Het account is aangemaakt maar er kon geen uitnodiging verstuurd worden omdat de e-mail service niet beschikbaar is."
    )

    def __call__(self, user, request):
        from sdg.accounts.models import UserInvitation

        UserInvitation.objects.create_and_send(user, request)

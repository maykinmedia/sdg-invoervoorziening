from django.utils.translation import ugettext_lazy as _

from sdg.core.events import EventFunction


class InviteUser(EventFunction):
    """Send an invitation to a user, setting the inviter as the request user."""

    exception_messages = {
        "default": _(
            "Het account kon niet worden aangemaakt omdat de e-mail service niet beschikbaar is."
        ),
        "admin": _(
            "Het account is aangemaakt maar er kon geen uitnodiging verstuurd worden omdat de e-mail service niet beschikbaar is."
        ),
    }

    def __call__(self, user, request):
        from sdg.accounts.models import UserInvitation

        UserInvitation.objects.create_and_send(user, request)

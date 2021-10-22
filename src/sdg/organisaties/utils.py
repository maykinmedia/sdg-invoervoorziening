def invite_user(user, request):
    """Send an invitation to a user, setting the inviter as the request user."""
    from sdg.accounts.models import UserInvitation

    UserInvitation.objects.create_and_send(user, request)

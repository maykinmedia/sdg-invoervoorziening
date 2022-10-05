from sdg.accounts.models import Role


def user_has_valid_roles(user, *, municipality, required_roles) -> bool:
    """
    Ensure user has at least one of the provided roles for a municipality.
    """
    try:
        role = user.roles.get(
            lokale_overheid=municipality,
        )
    except Role.DoesNotExist:
        return False

    if not any(getattr(role, r) for r in required_roles):
        return False

    return True

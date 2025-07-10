def hard_refresh_from_db(obj):
    """Retrieve the same object from database. Clears any annotations and cached properties."""
    obj.refresh_from_db()
    return obj.__class__.objects.get(pk=obj.pk)

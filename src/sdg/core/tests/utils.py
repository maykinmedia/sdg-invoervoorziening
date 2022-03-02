import contextlib
from copy import deepcopy


def hard_refresh_from_db(obj):
    """Retrieve the same object from database. Clears any annotations and cached properties."""
    obj.refresh_from_db()
    return obj.__class__.objects.get(pk=obj.pk)


@contextlib.contextmanager
def patch_event_register():
    """Allow safely modifying the event register during tests."""
    from sdg.core.events import event_register

    original_register = deepcopy(event_register)
    try:
        yield
    finally:
        for k, v in original_register.items():
            event_register[k] = v

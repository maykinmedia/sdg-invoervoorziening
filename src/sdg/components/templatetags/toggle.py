from django import template
import uuid

register = template.Library()


@register.inclusion_tag("components/toggle/toggle.html")
def toggle(label: str, checked: bool = False, **kwargs) -> dict:
    """
    A checkbox like toggle component, internally uses a checkbox.

    Args:
        - label: str - Label for the toggle, must be provided, may be hidden with hide_label.
        - checked: bool - Whether the initial value of the toggle is checked.

    Kwargs:
        - [id]: str - Id of the toggle (set on checkbox).
        - [icon_before]: str - Icon name to add before toggle.
        - [icon_after]: str - Icon name to add after toggle.
        - [name]: str - Name of the toggle (set on checkbox), defaults to id.
    """

    def get_id() -> str:
        """
        Returns either the given id or a random generated id.
        """
        return kwargs.get("id", f"toggle-{uuid.uuid1()}")

    def get_name() -> str:
        """
        Returns either the given name or the id.
        """
        return kwargs.get("name", get_id())

    return {
        **kwargs,
        "checked": checked,
        "id": get_id(),
        "label": label,
        "name": get_name(),
    }

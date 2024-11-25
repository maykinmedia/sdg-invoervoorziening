from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


class CaptureNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output
        return ""


@register.tag
def capture(parser, token):
    """
    Captures contents and assigns them to variable.
    Allows capturing templatetags that don't support "as".

    Example:

        {% capture as body %}{% lorem 20 w random %}{% endcapture %}
        {% include 'components/text/text.html' with body=body only %}
    """
    args = token.split_contents()
    if len(args) < 3 or args[-2] != "as":
        raise template.TemplateSyntaxError(
            "'capture' tag requires a variable name after keyword 'as'."
        )
    var_name = args[-1]
    nodelist = parser.parse(("endcapture",))
    parser.delete_first_token()
    return CaptureNode(nodelist, var_name)


@register.simple_tag
def placekitten(width=800, height=600):
    """
    Renders a "placekitten" placeholder image.

    Example:

        {%placekitten %}
        {%placekitten 200 200 %}
    """
    return format_html('<img src="{}" />'.format(placekitten_src(width, height)))


@register.simple_tag
def placekitten_src(width=800, height=600):
    """
    Return a "placekitten" placeholder image url.

    Example:

        {% placekitten_src as src %}
        {% placekitten_src 200 200 as mobile_src %}
        {% include 'components/image/image.html' with mobile_src=mobile_src src=src alt='placekitten' only %}
    """
    return "//placekitten.com/{}/{}".format(width, height)


@register.simple_tag
def version():
    return settings.RELEASE


@register.filter(name="addclass")
def addclass(field, class_attr):
    return field.as_widget(attrs={"class": class_attr})


@register.filter(name="addlabelclass")
def addlabelclass(field, class_attr):
    return field.as_widget(attrs={"class": class_attr, "placeholder": "Label"})


@register.filter(name="addlinkclass")
def addlinkclass(field, class_attr):
    return field.as_widget(attrs={"class": class_attr, "placeholder": "URL"})


@register.simple_tag
def template_dir(value):
    return dir(value)


@register.filter(name="notbool")
def notbool(true_value):
    return not true_value


@register.inclusion_tag("forms/field.html")
def field(field, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("forms/field_readonly.html")
def field_readonly(field, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("forms/choices_field.html")
def choices_field(field, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("forms/table_grid_field.html")
def table_grid_field(field, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("forms/checkbox.html")
def checkbox(field, **kwargs):
    return {**kwargs, "field": field}


@register.inclusion_tag("forms/status_icon.html")
def status_icon(status, **kwargs):
    return {**kwargs, "status": status}


@register.filter
def is_manager(user, local_government):
    """
    Usage: {{ user|is_manager:local_government }}
    """
    if user and local_government:
        return any(
            [
                role.is_beheerder
                for role in user.roles.all()
                if role.lokale_overheid == local_government
            ]
        )
    return None


@register.inclusion_tag("navigation/navigation.html", takes_context=True)
def navigation(context):
    """
    Navigation element.

    Args:
        - context
    """

    lokaleoverheid = context.get("lokaleoverheid")
    request = context.get("request")
    siteconfig = context.get("siteconfig")
    has_new_notifications = context.get("has_new_notifications")

    return {
        "context": context,
        "lokaleoverheid": lokaleoverheid,
        "request": request,
        "siteconfig": siteconfig,
        "has_new_notifications": has_new_notifications,
    }


@register.inclusion_tag("navigation/nav_item.html", takes_context=True)
def nav_item(context, href, title, **kwargs):
    """
    Generic nav_item element, built for the navigation component.

    Args:
        - context
        - link, href of the link
        - title, label of the link (can also be an <i> element)

    Kwargs:
        - icon, can be an <i> element.
        - id, set an id on the <a> element
        - blank_target, set the target to `_blank`
        - show_icon, boolean to render the icon
    """

    request = context.get("request")

    def check_active_link():
        if href == "/":
            # Equality operator instead of partial check (disables always true on home route)
            return href == request.path
        else:
            return href in request.path

    # Validate if the link is active.
    active_link = check_active_link()

    # Get kwargs vars.
    icon = kwargs.get("icon", None)
    show_icon = kwargs.get("show_icon", None)
    id = kwargs.get("id", None)
    blank_target = kwargs.get("blank_target", False)

    return {
        **kwargs,
        "context": context,
        "href": href,
        "title": title,
        "icon": icon,
        "show_icon": show_icon,
        "blank_target": blank_target,
        "id": id,
        "active_link": active_link,
    }


@register.inclusion_tag("navigation/user_dropdown.html", takes_context=True)
def user_dropdown(context):
    """
    Dropdown element inside the header.

    Args:
        - context
    """

    lokaleoverheid = context.get("lokaleoverheid")
    request = context.get("request")

    role_pk = None
    if lokaleoverheid:
        role_pk = (
            request.user.roles.all()
            .get(lokale_overheid=lokaleoverheid, user=request.user)
            .pk
        )

    return {
        "context": context,
        "lokaleoverheid": lokaleoverheid,
        "request": request,
        "role_pk": role_pk,
    }

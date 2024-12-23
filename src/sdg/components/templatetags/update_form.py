from django import template
from django.forms import BaseForm, BaseFormSet

from sdg.conf.utils import org_type_cfg
from sdg.producten.utils import get_fields, get_languages

register = template.Library()


@register.inclusion_tag(
    "components/update_form/update_form_generic.html", takes_context=True
)
def update_form_generic(context) -> dict:
    """
    Generic form (readonly), built for update view.

    Args:
        - context
        - product as generic_products
    """
    # Define the name of the form
    form_name = "form__generic"

    # Get some properties from the context
    generic_products = context.get("generic_products")
    formset = context.get("formset")

    readonly = not context['user_can_edit']

    def get_object_list():
        obj_list = []

        fields = generic_products[0].template_fields

        for index, field in enumerate(fields):
            obj = {
                "bound_fields": [
                    product.template_fields[index] for product in generic_products
                ],
                "field_name": field.name,
            }

            for index, language in enumerate(get_languages(formset)):
                obj["bound_fields"][index].language = language
                obj["bound_fields"][index].landelijke_link = generic_products[
                    index
                ].landelijke_link

            obj_list.append(obj)

        return obj_list

    return {
        "context": context,
        "form_name": form_name,
        "object_list": get_object_list(),
        "readonly": readonly,
    }


@register.inclusion_tag(
    "components/update_form/update_form_specific.html", takes_context=True
)
def update_form_specific(context) -> dict:
    """
    Specific form, built for update view.

    Args:
        - context
    """
    # Define the name of the form
    form_name = "form__specific"

    # Get some properties from the context
    localized_form_fields = context.get("localized_form_fields")
    formset: BaseFormSet = context.get("formset")

    # Get languages and fields form utils functions.
    languages = get_languages(formset)
    fields = get_fields(formset.forms[0], localized_form_fields)

    readonly = not context['user_can_edit']

    def get_object_list(formset: BaseFormSet, fields: list) -> list:
        object_list = []
        for field in fields:
            obj = {
                "bound_fields": [form[field] for form in formset.forms],
                "field": field,
            }
            for index, language in enumerate(languages):
                obj["bound_fields"][index].language = language
            object_list.append(obj)
        return object_list

    return {
        "context": context,
        "form": formset,
        "form_name": form_name,
        "object_list": get_object_list(formset, fields),
        "readonly": readonly,
        "org_type_name": org_type_cfg().name
    }


@register.inclusion_tag(
    "components/update_form/update_form_general.html", takes_context=True
)
def update_form_general(context) -> dict:
    """
    General form, built for update view.

    Args:
        - context
    """
    # Define the name of the form
    form_name = "form__general"

    # Get some properties from the context
    areas = context.get("areas")
    doelgroep = context.get("doelgroep")
    formset: BaseFormSet = context.get("formset")
    product = context.get("product")
    product_form = context.get("product_form")
    version_form: BaseForm = context.get("version_form")

    # Get the used languages in the formset
    languages = get_languages(formset)

    # Localized fields in the general update form
    localized_field_names = [
        "product_aanwezig_toelichting",
        "product_valt_onder_toelichting",
    ]
    localized_fields = get_fields(formset.forms[0], localized_field_names)

    # Nonlocalized fields in the general update form
    nonlocalized_field_names = ["interne_opmerkingen"]
    nonlocalized_fields = get_fields(version_form, nonlocalized_field_names)
    readonly = not context['user_can_edit']


    def get_localized_object_dict(formset: BaseFormSet, fields: list) -> dict:
        object_list = {}
        for field in fields:
            obj = {
                "bound_fields": [form[field] for form in formset.forms],
                "field": field,
            }
            for index, language in enumerate(languages):
                obj["bound_fields"][index].language = language
            object_list[field] = obj
        return object_list

    def get_nonlocalized_object_dict(form: BaseForm, fields: list) -> dict:
        object_list = {}
        for field in fields:
            obj = {
                "bound_fields": [form[field]],
                "field": field,
            }
            object_list[field] = obj
        return object_list

    return {
        "areas": areas,
        "context": context,
        "doelgroep": doelgroep,
        "form_name": form_name,
        "localized_object_dict": get_localized_object_dict(formset, localized_fields),
        "nonlocalized_object_dict": get_nonlocalized_object_dict(
            version_form, nonlocalized_fields
        ),
        "product_form": product_form,
        "product": product,
        "readonly": readonly
    }

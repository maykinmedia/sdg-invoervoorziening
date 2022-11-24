from itertools import chain

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.checks import Error, Tags, register

from glom import glom


@register(Tags.models)
def localized_form_field_check(app_configs, **kwargs):
    errors = []

    LocalizedProductFieldConfiguration = apps.get_model(
        "core", "LocalizedProductFieldConfiguration"
    )
    ProductFieldConfiguration = apps.get_model("core", "ProductFieldConfiguration")

    # Ensure all fields are exposed in the admin
    registry_inline = admin.site._registry[ProductFieldConfiguration].inlines[0]
    admin_fields = [
        glom(fieldset, "1.fields") for fieldset in registry_inline.fieldsets
    ]
    admin_fields = list(chain(*admin_fields))

    for field in settings.SDG_LOCALIZED_FORM_FIELDS:
        field_name = f"localizedproduct_{field}"
        # Ensure field is in the config model
        if not hasattr(LocalizedProductFieldConfiguration, field_name):
            errors.append(
                Error(
                    f"LocalizedProductFieldConfiguration is missing a field for {field_name}",
                    hint=f"Add a field named localizedproduct_{field_name}",
                    obj=LocalizedProductFieldConfiguration,
                    id="localizedproduct.E001",
                )
            )

        # Ensure field is registered in the admin
        if field_name not in admin_fields:
            errors.append(
                Error(
                    f"Field {field_name} is not registered in the admin",
                    hint=f"Add {field_name} to the admin",
                    obj=LocalizedProductFieldConfiguration,
                    id="localizedproduct.E002",
                )
            )

    return errors

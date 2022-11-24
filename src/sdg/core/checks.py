from django.apps import apps
from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.models)
def localized_form_field_check(app_configs, **kwargs):
    errors = []

    localized_field_config = apps.get_model(
        "core", "LocalizedProductFieldConfiguration"
    )

    for field in settings.SDG_LOCALIZED_FORM_FIELDS:
        if not hasattr(localized_field_config, f"localizedproduct_{field}"):
            errors.append(
                Error(
                    "LocalizedProductFieldConfiguration is missing a field for %s"
                    % field,
                    hint="Add a field named localizedproduct_%s" % field,
                    obj=localized_field_config,
                    id="localizedproduct.E001",
                )
            )

    return errors

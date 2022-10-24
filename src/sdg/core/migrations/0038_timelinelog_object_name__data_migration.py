# Generated by Django 3.2.13 on 2022-10-20 17:37

from django.db import migrations
from django.utils.translation import gettext as _


def _get_pretty_version(instance):
    concept = "" if instance.publicatie_datum else "(concept)"
    return f"{instance.versie} {concept}".strip()


def _get_pretty_name__version(instance):
    try:
        product_name = instance.product.generiek_product.upn.upn_label
        return f"{product_name} — versie {_get_pretty_version(instance)}"
    except instance._meta.model.product.RelatedObjectDoesNotExist:
        return f"Unknown product - versie {_get_pretty_version(instance)}"


def _get_pretty_name__municipality(instance):
    if instance.organisatie.owms_end_date:
        return _("{label} (opgeheven op {end_date})").format(
            label=instance.organisatie.owms_pref_label,
            end_date=instance.organisatie.owms_end_date.date(),
        )
    return instance.organisatie.owms_pref_label


name_gen_mapping = {
    "productversie": _get_pretty_name__version,
    "lokaleoverheid": _get_pretty_name__municipality,
}


def update_existing_timelinelogs(apps, schema_editor):
    TimelineLog = apps.get_model("timeline_logger", "TimelineLog")
    for log in TimelineLog.objects.all():
        Model = apps.get_model(log.content_type.app_label, log.content_type.model)
        try:
            instance = Model.objects.get(pk=log.object_id)
            log.extra_data["object_name"] = name_gen_mapping.get(
                log.content_type.model,
                lambda instance: f"{instance._meta.verbose_name} {instance.pk}",
            )(instance)
        except Model.DoesNotExist:
            log.extra_data["object_name"] = "<Deleted object>"
        log.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_productfieldconfiguration_productversie_interne_opmerkingen"),
        ("timeline_logger", "0006_auto_20220413_0749"),
    ]

    operations = [
        migrations.RunPython(update_existing_timelinelogs),
    ]

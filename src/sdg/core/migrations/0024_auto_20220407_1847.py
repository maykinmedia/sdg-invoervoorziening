# Generated by Django 2.2.25 on 2022-04-07 18:47

from django.db import migrations
from django.db.models import Count


def clean_up_ig_and_themas(apps, schema_editor):
    Thema = apps.get_model("core", "Thema")
    Informatiegebied = apps.get_model("core", "Informatiegebied")

    for thema in list(Thema.objects.all()):
        thema.code = thema.thema_uri.rsplit("_")[-1]
        thema.informatiegebied = (
            Informatiegebied.objects.filter(
                informatiegebied_uri=thema.informatiegebied.informatiegebied_uri
            )
            .order_by("code")
            .first()
        )
        thema.save()

    Informatiegebied.objects.annotate(thema_count=Count("thema")).filter(
        thema_count=0
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_auto_20220407_1905"),
    ]

    operations = [
        migrations.RunPython(clean_up_ig_and_themas, migrations.RunPython.noop),
    ]

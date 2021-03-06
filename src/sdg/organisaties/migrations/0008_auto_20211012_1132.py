# Generated by Django 2.2.24 on 2021-10-12 11:32

from django.db import migrations, models


def update_existing_opening_times(apps, schema_editor):
    LokaleOverheid = apps.get_model("organisaties", "LokaleOverheid")

    LokaleOverheid.objects.filter(contact_emailadres=None).update(contact_emailadres="")
    LokaleOverheid.objects.filter(contact_telefoonnummer=None).update(
        contact_telefoonnummer=""
    )
    LokaleOverheid.objects.filter(contact_website=None).update(contact_website="")


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0007_merge_20211007_1658"),
    ]

    operations = [
        migrations.RunPython(update_existing_opening_times),
    ]

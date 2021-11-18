# Generated by Django 2.2.24 on 2021-11-08 15:54

from django.db import migrations, models
import uuid


def create_uuid(apps, schema_editor):
    Lokatie = apps.get_model("organisaties", "Lokatie")
    LokaleOverheid = apps.get_model("organisaties", "LokaleOverheid")
    for obj in LokaleOverheid.objects.all():
        obj.uuid = uuid.uuid4()
        obj.save()
    for obj in Lokatie.objects.all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0011_auto_20211108_1407"),
    ]

    operations = [
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
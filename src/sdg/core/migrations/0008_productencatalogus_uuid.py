# Generated by Django 2.2.24 on 2021-11-08 14:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_auto_20211012_1132"),
    ]

    operations = [
        migrations.AddField(
            model_name="productencatalogus",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]

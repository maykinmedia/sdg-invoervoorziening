# Generated by Django 2.2.24 on 2022-01-19 15:39

from django.db import migrations, models
import sdg.producten.models.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0017_auto_20211220_1223"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="localizedproduct",
            name="decentrale_link",
        ),
    ]
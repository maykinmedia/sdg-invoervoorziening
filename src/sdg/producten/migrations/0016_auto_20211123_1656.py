# Generated by Django 2.2.24 on 2021-11-23 16:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0015_merge_20211118_1435"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="localizedproduct",
            name="specifieke_link",
        ),
    ]

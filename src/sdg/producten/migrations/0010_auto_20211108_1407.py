# Generated by Django 2.2.24 on 2021-11-08 14:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0009_auto_20211026_1227"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]

# Generated by Django 3.2.16 on 2022-11-24 15:34

import django.contrib.postgres.fields
from django.db import migrations, models
import sdg.core.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0040_merge_20221027_1545"),
    ]

    operations = [
        migrations.AddField(
            model_name="localizedproductfieldconfiguration",
            name="localizedproduct_decentrale_procedure_label",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Decentrale procedure label",
            ),
        ),
    ]

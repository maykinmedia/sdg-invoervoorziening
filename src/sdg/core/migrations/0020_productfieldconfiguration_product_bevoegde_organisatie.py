# Generated by Django 2.2.25 on 2022-03-24 12:21

import django.contrib.postgres.fields
from django.db import migrations, models
import sdg.core.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_auto_20220304_1802"),
    ]

    operations = [
        migrations.AddField(
            model_name="productfieldconfiguration",
            name="product_bevoegde_organisatie",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Algemene bevoegde organisatie",
            ),
        ),
    ]
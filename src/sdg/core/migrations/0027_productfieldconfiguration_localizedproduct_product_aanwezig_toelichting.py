# Generated by Django 2.2.25 on 2022-04-21 14:13

import django.contrib.postgres.fields
from django.db import migrations, models
import sdg.core.db.fields


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0026_remove_productfieldconfiguration_product_product_aanwezig_toelichting",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_aanwezig_toelichting",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Algemene aanwezigheid toelichting",
            ),
        ),
    ]
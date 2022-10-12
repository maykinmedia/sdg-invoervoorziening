# Generated by Django 3.2.13 on 2022-10-03 14:33

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0037_localizedproduct_decentrale_procedure_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="productversie",
            name="bewerkte_velden",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, default=dict, verbose_name="bewerkte_velden"
            ),
        ),
        migrations.AddField(
            model_name="productversie",
            name="interne_opmerkingen",
            field=models.TextField(
                blank=True,
                help_text="Interne opmerkingen die niet zichtbaar zijn buiten deze omgeving.",
                verbose_name="interne opmerkingen",
            ),
        ),
    ]
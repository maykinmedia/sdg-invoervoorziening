# Generated by Django 3.2.16 on 2022-11-30 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0042_alter_generiekproduct_doelgroep"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="api_verborgen",
            field=models.BooleanField(
                default=False,
                help_text="Verbergen voor Nationale Portalen.",
                verbose_name="verborgen",
            ),
        ),
    ]

# Generated by Django 2.2.24 on 2021-09-29 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_auto_20210927_1722"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productencatalogus",
            name="naam",
            field=models.CharField(
                help_text="De naam van de producten catalogus.",
                max_length=120,
                verbose_name="naam",
            ),
        ),
    ]

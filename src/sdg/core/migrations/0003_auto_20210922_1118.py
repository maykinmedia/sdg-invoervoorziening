# Generated by Django 2.2.24 on 2021-09-22 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_auto_20210921_1844"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="productencatalogus",
            constraint=models.UniqueConstraint(
                fields=("referentie_catalogus", "lokale_overheid"),
                name="unique_referentie_catalogus_and_lokale_overheid",
            ),
        ),
    ]
# Generated by Django 3.2.23 on 2025-04-01 21:05

from django.db import migrations, models
import sdg.producten.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0064_alter_localizedproduct_verwijzing_links"),
    ]

    operations = [
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="landelijke_link",
            field=models.URLField(
                blank=True,
                help_text="URL van de productpagina wanneer het een landelijk product betreft of de pagina met enkel generieke beschrijving van een decentraal product, bijvoorbeeld : https://ondernemersplein.overheid.nl/terrasvergunning. gebruikt voor o.a. notificeren, feedback & statistics en het kunnen bekijken van de generieke productinformatie (bv door gebruikers van de organisatie invoervoorziening) ",
                validators=[sdg.producten.models.validators.validate_https],
                verbose_name="landelijke link",
            ),
        ),
    ]

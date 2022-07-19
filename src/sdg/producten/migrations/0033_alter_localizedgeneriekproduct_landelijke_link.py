# Generated by Django 3.2.13 on 2022-07-21 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0032_alter_product_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="landelijke_link",
            field=models.URLField(
                help_text="URL van de productpagina wanneer het een landelijk product betreft of de pagina met enkel generieke beschrijving van een decentraal product, bijvoorbeeld : https://ondernemersplein.kvk.nl/terrasvergunning. gebruikt voor o.a. notificeren, feedback & statistics en het kunnen bekijken van de generieke productinformatie (bv door gebruikers van de organisatie invoervoorziening) ",
                verbose_name="landelijke link",
            ),
        ),
    ]

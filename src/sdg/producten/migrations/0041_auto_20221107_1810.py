# Generated by Django 3.2.13 on 2022-11-07 18:10

from django.db import migrations, models
import sdg.producten.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0040_auto_20221031_1251"),
    ]

    operations = [
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="generieke_tekst",
            field=sdg.producten.models.fields.MarkdownxField(
                blank=True,
                help_text="De Nationale Portalen schrijven een inleidende, algemene tekst over het product. Dit veld ondersteund Markdown.",
                verbose_name="generieke tekst",
            ),
        ),
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="korte_omschrijving",
            field=models.CharField(
                blank=True,
                help_text='Korte omschrijving van wat er op de pagina staat, gebruikt in de meta tags van de productpagina (meta name="description"). Deze tekst wordt gebruikt om te tonen wanneer de pagina wordt gevonden in een zoekmachine. ',
                max_length=160,
                verbose_name="korte omschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="landelijke_link",
            field=models.URLField(
                blank=True,
                help_text="URL van de productpagina wanneer het een landelijk product betreft of de pagina met enkel generieke beschrijving van een decentraal product, bijvoorbeeld : https://ondernemersplein.kvk.nl/terrasvergunning. gebruikt voor o.a. notificeren, feedback & statistics en het kunnen bekijken van de generieke productinformatie (bv door gebruikers van de organisatie invoervoorziening) ",
                verbose_name="landelijke link",
            ),
        ),
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="product_titel",
            field=models.CharField(
                blank=True,
                help_text="De titel van het decentrale product, die immers kan afwijken van de landelijke titel.",
                max_length=100,
                verbose_name="product titel",
            ),
        ),
    ]
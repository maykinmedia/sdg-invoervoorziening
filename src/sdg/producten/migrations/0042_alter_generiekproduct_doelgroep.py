# Generated by Django 3.2.16 on 2022-11-24 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0041_auto_20221107_1810"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generiekproduct",
            name="doelgroep",
            field=models.CharField(
                blank=True,
                choices=[("eu-burger", "EU Burger"), ("eu-bedrijf", "EU Bedrijf")],
                help_text="Geeft aan voor welke doelgroep het product is bedoeld: burgers, bedrijven of burgers en bedrijven. Wordt gebruikt wanneer een portaal informatie over het product ophaalt uit de invoervoorziening. Zo krijgen de ondernemersportalen de ondernemersvariant en de burgerportalen de burgervariant. ",
                max_length=32,
            ),
        ),
    ]

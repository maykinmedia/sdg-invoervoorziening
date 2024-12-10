# Generated by Django 3.2.23 on 2024-11-26 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0058_alter_localizedproduct_decentrale_procedure_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="automatisch_doordrukken",
            field=models.BooleanField(
                default=False,
                help_text="Selecteer of het product (referentie) teksten automatisch moet worden doorgedrukt naar de specifieke producten.",
                verbose_name="Product teksten automatisch doordrukken",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="automatisch_doordrukken_datum",
            field=models.DateField(
                blank=True,
                help_text="Deze datum is 30 dagen na de publicatie datum, wanneer de optie 'Automatisch doordrukken' op 'Ja' geselecteerd.",
                null=True,
                verbose_name="Datum waarop de tekst automatisch word doorgedrukt",
            ),
        ),
    ]

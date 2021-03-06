# Generated by Django 2.2.24 on 2022-01-22 15:51

from django.db import migrations, models
import django.db.models.deletion
import sdg.core.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0014_lokatie_openingstijden_opmerking"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="lokatie",
            options={"verbose_name": "locatie", "verbose_name_plural": "locaties"},
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="land",
            field=models.CharField(
                help_text="Het land van de locatie.",
                max_length=128,
                verbose_name="land",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="lokale_overheid",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="locaties",
                to="organisaties.LokaleOverheid",
                verbose_name="lokale overheid",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="naam",
            field=models.CharField(
                help_text="De naam van de locatie.", max_length=40, verbose_name="naam"
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="nummer",
            field=models.PositiveIntegerField(
                help_text="Het huisnummer van de locatie.", verbose_name="nummer"
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="plaats",
            field=models.CharField(
                help_text="De plaatsnaam van de locatie.",
                max_length=256,
                verbose_name="plaats",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="postcode",
            field=models.CharField(
                help_text="De postcode van de locatie.",
                max_length=6,
                validators=[sdg.core.models.validators.validate_postcode],
                verbose_name="postcode",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="straat",
            field=models.CharField(
                help_text="De straatnaam van de locatie.",
                max_length=256,
                verbose_name="straat",
            ),
        ),
    ]

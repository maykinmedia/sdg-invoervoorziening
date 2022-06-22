# Generated by Django 3.2.13 on 2022-06-22 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0021_alter_lokatie_nummer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_emailadres",
            field=models.EmailField(
                blank=True,
                help_text="Het algemene e-mailadres van de gemeente of het e-mailadres van het klantcontactcentrum van de gemeente.",
                max_length=254,
                verbose_name="contact emailadres",
            ),
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_telefoonnummer",
            field=models.CharField(
                blank=True,
                help_text="Het internationale telefoonnummer waarop de gemeente bereikbaar is. Bijvoorbeeld: +31 20 624 1111",
                max_length=20,
                verbose_name="contact telefoonnummer",
            ),
        ),
    ]

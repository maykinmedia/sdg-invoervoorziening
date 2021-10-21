# Generated by Django 2.2.24 on 2021-10-12 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0008_auto_20211012_1132"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_emailadres",
            field=models.EmailField(
                blank=True,
                default="",
                help_text="Het e-mailadres van de verantwoordelijke contactpersoon.",
                max_length=254,
                verbose_name="contact emailadres",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_telefoonnummer",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Het telefoonnummer van de verantwoordelijke contactpersoon.",
                max_length=20,
                verbose_name="contact telefoonnummer",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_website",
            field=models.URLField(
                blank=True,
                default="",
                help_text="De website van de verantwoordelijke contactpersoon.",
                verbose_name="contact website",
            ),
            preserve_default=False,
        ),
    ]
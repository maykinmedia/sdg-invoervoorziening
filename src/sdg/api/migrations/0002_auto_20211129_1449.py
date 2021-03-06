# Generated by Django 2.2.24 on 2021-11-29 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="token",
            name="administration",
            field=models.CharField(
                blank=True,
                help_text="Naam van de administratie",
                max_length=100,
                verbose_name="administratie",
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="application",
            field=models.CharField(
                blank=True,
                help_text="Naam van de applicatie",
                max_length=100,
                verbose_name="applicatie",
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="contact_person",
            field=models.CharField(
                default="person",
                help_text="Naam van de contactpersoon",
                max_length=100,
                verbose_name="contactpersoon",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="token",
            name="email",
            field=models.EmailField(
                default="test@email.com",
                help_text="Email van de contactpersoon",
                max_length=254,
                verbose_name="email",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="token",
            name="modified",
            field=models.DateTimeField(
                auto_now=True,
                help_text="Wanneer het token is aangepast",
                verbose_name="aangepast",
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="organization",
            field=models.CharField(
                blank=True,
                help_text="Naam van de organisatie",
                max_length=100,
                verbose_name="organisatie",
            ),
        ),
        migrations.AlterField(
            model_name="token",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Wanneer het token is aangemaakt",
                verbose_name="aangemaakt",
            ),
        ),
    ]

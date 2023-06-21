# Generated by Django 3.2.16 on 2023-04-12 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0045_generate_overheids_organisatie_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="overheidsorganisatie",
            name="dpc_slug",
            field=models.SlugField(
                blank=True,
                help_text="De gemeente slug voor de Nederland wereldwijd website gebaseerd op het OWMS pref label.",
                max_length=220,
                verbose_name="Nederland wereldwijd slug field",
            ),
        ),
    ]
# Generated by Django 3.2.13 on 2022-10-21 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_auto_20220122_1516"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ("first_name", "last_name"),
                "verbose_name": "gebruiker",
                "verbose_name_plural": "gebruikers",
            },
        ),
    ]

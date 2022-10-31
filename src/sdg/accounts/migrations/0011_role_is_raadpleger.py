# Generated by Django 3.2.13 on 2022-10-05 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_auto_20220122_1516"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="is_raadpleger",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user is a viewer of a specific overheidsorganisatie. ",
                verbose_name="raadpleger",
            ),
        ),
    ]
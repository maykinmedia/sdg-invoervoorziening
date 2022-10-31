# Generated by Django 3.2.13 on 2022-10-31 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_merge_0011_alter_user_options_0011_role_is_raadpleger"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="is_raadpleger",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user is a consultant of a specific overheidsorganisatie. ",
                verbose_name="raadpleger",
            ),
        ),
    ]
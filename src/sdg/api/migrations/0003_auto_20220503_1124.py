# Generated by Django 2.2.25 on 2022-05-03 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_auto_20211129_1449"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="token",
            options={
                "ordering": ["contact_person", "organization"],
                "verbose_name": "token",
                "verbose_name_plural": "tokens",
            },
        ),
    ]

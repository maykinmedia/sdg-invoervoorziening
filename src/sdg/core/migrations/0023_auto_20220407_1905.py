# Generated by Django 2.2.25 on 2022-04-07 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_merge_20220324_1603"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informatiegebied",
            name="informatiegebied",
            field=models.CharField(
                help_text="Het bij de gegevens behorende SDG informatiegebied.",
                max_length=80,
                verbose_name="informatiegebied",
            ),
        ),
        migrations.AlterField(
            model_name="informatiegebied",
            name="informatiegebied_uri",
            field=models.URLField(
                help_text="Informatiegebied SDG URI van landelijk product",
                verbose_name="informatiegebied URI",
            ),
        ),
        migrations.AddField(
            model_name="thema",
            name="code",
            field=models.CharField(
                default="XX",
                help_text="De SDG code van het desbetreffende informatiegebied.",
                max_length=32,
                verbose_name="code",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="thema",
            name="thema",
            field=models.CharField(
                help_text="Het SDG thema dat verband houdt met de gegevens.",
                max_length=512,
                verbose_name="thema",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="thema_uri",
            field=models.URLField(
                help_text="SDG thema URI van landelijk product",
                unique=True,
                verbose_name="thema uri",
            ),
        ),
    ]

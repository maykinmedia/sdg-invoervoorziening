# Generated by Django 2.2.24 on 2021-10-06 10:45

from django.db import migrations, models
import sdg.core.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0002_auto_20210927_1722"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lokatie",
            name="dinsdag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="dinsdag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="donderdag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="donderdag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="maandag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="maandag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="vrijdag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="vrijdag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="woensdag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="woensdag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="zaterdag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="zaterdag",
            ),
        ),
        migrations.AlterField(
            model_name="lokatie",
            name="zondag",
            field=models.CharField(
                blank=True,
                max_length=80,
                null=True,
                validators=[sdg.core.models.validators.validate_openingstijden],
                verbose_name="zondag",
            ),
        ),
    ]
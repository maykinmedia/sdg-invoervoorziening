# Generated by Django 3.2.13 on 2022-05-24 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0021_alter_lokatie_nummer"),
        ("api", "0002_auto_20211129_1449"),
    ]

    operations = [
        migrations.CreateModel(
            name="TokenAuthorization",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "lokale_overheid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="organisaties.lokaleoverheid",
                    ),
                ),
                (
                    "token",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.token",
                    ),
                ),
            ],
            options={
                "verbose_name": "Betreffende Overheid",
                "verbose_name_plural": "Betreffende Overheiden",
            },
        ),
    ]
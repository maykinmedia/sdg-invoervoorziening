# Generated by Django 2.2.25 on 2022-03-24 12:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_productfieldconfiguration_product_bevoegde_organisatie"),
        ("organisaties", "0016_auto_20220126_1722"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lokaleoverheid",
            name="bevoegde_organisatie",
        ),
        migrations.RemoveField(
            model_name="lokaleoverheid",
            name="verantwoordelijke_organisatie",
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_telefoonnummer",
            field=models.CharField(
                blank=True,
                help_text="Het telefoonnummer van de gemeente.",
                max_length=20,
                verbose_name="contact telefoonnummer",
            ),
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_website",
            field=models.URLField(
                blank=True,
                help_text="Website van de gemeente.",
                verbose_name="contact website",
            ),
        ),
        migrations.CreateModel(
            name="BevoegdeOrganisatie",
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
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="De identificatie die binnen deze API gebruikt wordt voor de resource.",
                        unique=True,
                        verbose_name="UUID",
                    ),
                ),
                ("naam", models.CharField(max_length=255, verbose_name="naam")),
                (
                    "lokale_overheid",
                    models.ForeignKey(
                        help_text="De lokale overheid waartoe deze bevoegde organisatie behoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bevoegde_organisaties",
                        to="organisaties.LokaleOverheid",
                        verbose_name="lokale overheid",
                    ),
                ),
                (
                    "organisatie",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bevoegde_organisaties",
                        to="core.Overheidsorganisatie",
                        verbose_name="organisatie",
                    ),
                ),
            ],
            options={
                "verbose_name": "bevoegde organisatie",
                "verbose_name_plural": "bevoegde organisaties",
            },
        ),
    ]

# Generated by Django 2.2.24 on 2021-09-28 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("producten", "0002_auto_20210924_1819"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="publicatie_datum",
        ),
        migrations.RemoveField(
            model_name="product",
            name="versie",
        ),
        migrations.AlterField(
            model_name="productuitvoering",
            name="product",
            field=models.ForeignKey(
                help_text="Het product voor het productuitvoering.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="uitvoeringen",
                to="producten.Product",
                verbose_name="product",
            ),
        ),
        migrations.CreateModel(
            name="ProductVersie",
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
                    "versie",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Het versienummer van het product.",
                        verbose_name="versie",
                    ),
                ),
                (
                    "publicatie_datum",
                    models.DateTimeField(
                        help_text="De datum van publicatie van de productversie.",
                        verbose_name="publicatie datum",
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "gemaakt_op",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="De oorspronkelijke aanmaakdatum voor deze productversie.",
                        verbose_name="gemaakt op",
                    ),
                ),
                (
                    "gewijzigd_op",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="De wijzigingsdatum voor deze productversie.",
                        verbose_name="gewijzigd op",
                    ),
                ),
                (
                    "gemaakt_door",
                    models.ForeignKey(
                        help_text="De maker van deze productversie.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="productversies",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="crea",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        help_text="Het product voor het product versie.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="versies",
                        to="producten.Product",
                        verbose_name="product",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="localizedproduct",
            name="product_versie",
            field=models.ForeignKey(
                help_text="Het specifieke product van deze vertaling.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vertalingen",
                to="producten.ProductVersie",
                verbose_name="product versie",
                null=True,
            ),
        ),
    ]

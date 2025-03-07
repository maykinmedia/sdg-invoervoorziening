# Generated by Django 3.2.23 on 2024-11-05 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0058_alter_localizedproduct_decentrale_procedure_link"),
    ]

    operations = [
        migrations.CreateModel(
            name="BrokenLinks",
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
                ("url", models.URLField(default="")),
                ("error_count", models.PositiveIntegerField(default=0)),
                ("last_checked", models.DateTimeField(auto_now=True)),
                ("occuring_field", models.TextField(default="")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="producten.product",
                    ),
                ),
            ],
        ),
    ]

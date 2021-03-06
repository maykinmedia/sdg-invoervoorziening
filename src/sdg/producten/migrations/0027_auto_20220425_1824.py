# Generated by Django 2.2.25 on 2022-04-25 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0026_auto_20220425_1824"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("generiek_product__isnull", False),
                        ("referentie_product__isnull", True),
                    ),
                    models.Q(
                        ("generiek_product__isnull", True),
                        ("referentie_product__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="generic_or_reference",
            ),
        ),
    ]

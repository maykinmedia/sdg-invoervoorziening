# Generated by Django 2.2.24 on 2021-11-18 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0012_merge_20211116_1604"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_aanwezig",
            field=models.BooleanField(
                blank=True,
                help_text="Voert u dit product?",
                null=True,
                verbose_name="product aanwezig",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="product_aanwezig_toelichting",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Toelichting",
                verbose_name="product aanwezig toelichting",
            ),
        ),
    ]

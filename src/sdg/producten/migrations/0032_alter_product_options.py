# Generated by Django 3.2.13 on 2022-05-24 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0031_auto_20220506_1816"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ["generiek_product__upn__upn_label"],
                "verbose_name": "product",
                "verbose_name_plural": "producten",
            },
        ),
    ]

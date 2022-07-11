# Generated by Django 3.2.13 on 2022-07-06 16:06

from django.db import migrations


def set_is_default_catalogus_true(apps, schema_editor):
    ProductenCatalogus = apps.get_model("core", "ProductenCatalogus")

    new_producten_catalogus_list = []
    for catalogus in ProductenCatalogus.objects.all():
        new_producten_catalogus_list.append(
            ProductenCatalogus(
                is_default_catalogus=True,
                uuid=catalogus.uuid,
                pk=catalogus.pk,
            )
        )

    ProductenCatalogus.objects.bulk_update(
        new_producten_catalogus_list, ["is_default_catalogus"]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0031_productencatalogus_is_default_catalogus"),
    ]

    operations = [
        migrations.RunPython(set_is_default_catalogus_true, migrations.RunPython.noop),
    ]
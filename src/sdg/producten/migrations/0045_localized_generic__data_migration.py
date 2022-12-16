from functools import partial

from django.db import migrations


def format_verwijzing_links(verwijzing_links, reverse):
    if reverse:
        target = 2
        transform: callable = lambda x: x.pop()
    else:
        target = 3
        transform: callable = lambda x: x.append("")

    if not verwijzing_links:
        return []

    if all(len(i) == target for i in verwijzing_links):
        return verwijzing_links

    for i in verwijzing_links:
        while len(i) != target:
            transform(i)

    return verwijzing_links


def exec_generic_data_migration(apps, schema_editor, reverse=False):
    LocalizedGeneriekProduct = apps.get_model("producten", "LocalizedGeneriekProduct")

    for obj in LocalizedGeneriekProduct.objects.all():
        obj.verwijzing_links = format_verwijzing_links(obj.verwijzing_links, reverse)
        obj.save()


exec_generic_data_migration_reverse = partial(exec_generic_data_migration, reverse=True)


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0044_auto_20221216_1601"),
    ]

    operations = [
        migrations.RunPython(
            exec_generic_data_migration, exec_generic_data_migration_reverse
        ),
    ]

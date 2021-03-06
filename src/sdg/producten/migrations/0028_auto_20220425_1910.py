# Generated by Django 2.2.25 on 2022-04-25 19:10

from django.db import migrations


def fix_authorized_orgs(apps, schema_editor):
    Product = apps.get_model("producten", "Product")
    BevoegdeOrganisatie = apps.get_model("organisaties", "BevoegdeOrganisatie")

    for product in list(Product.objects.filter(bevoegde_organisatie=None)):

        default_auth_org = BevoegdeOrganisatie.objects.filter(
            lokale_overheid=product.catalogus.lokale_overheid
        ).first()
        # Fix missing default authorized organisation.
        if default_auth_org is None:
            default_auth_org = BevoegdeOrganisatie.objects.create(
                lokale_overheid=product.catalogus.lokale_overheid,
                organisatie=product.catalogus.lokale_overheid.organisatie,
            )

        product.bevoegde_organisatie = default_auth_org
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0027_auto_20220425_1824"),
    ]

    operations = [
        migrations.RunPython(fix_authorized_orgs, migrations.RunPython.noop),
    ]

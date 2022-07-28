# Generated by Django 3.2.13 on 2022-07-29 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_create_and_migrate_field_configuration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="localizedproductfieldconfiguration",
            options={
                "ordering": ["-taal"],
                "verbose_name": "Vertaalde configuratie",
                "verbose_name_plural": "Vertaalde configuraties",
            },
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_datum_check",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_generieke_tekst",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_korte_omschrijving",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_landelijke_link",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_product_titel",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_verwijzing_links",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_bewijs",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_bezwaar_en_beroep",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_datum_wijziging",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_decentrale_link",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_decentrale_procedure_link",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_kosten_en_betaalmethoden",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_procedure_beschrijving",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_aanwezig_toelichting",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_titel_decentraal",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_valt_onder_toelichting",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_specifieke_tekst",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_uiterste_termijn",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_vereisten",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_verwijzing_links",
        ),
        migrations.RemoveField(
            model_name="productfieldconfiguration",
            name="localizedproduct_wtd_bij_geen_reactie",
        ),
    ]

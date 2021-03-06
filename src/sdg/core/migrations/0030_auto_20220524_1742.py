# Generated by Django 3.2.13 on 2022-05-24 17:42

import django.contrib.postgres.fields
from django.db import migrations, models
import sdg.core.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0029_alter_informatiegebied_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_datum_check",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Datum check",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_korte_omschrijving",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Korte omschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_landelijke_link",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Landelijke link",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_product_titel",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product titel",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedgeneriekproduct_verwijzing_links",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Verwijzing links",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_bewijs",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Bewijs",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_bezwaar_en_beroep",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Bezwaar en beroep",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_datum_wijziging",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Datum wijziging",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_decentrale_link",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Decentrale link",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_decentrale_procedure_link",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Decentrale procedure link",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_kosten_en_betaalmethoden",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Kosten en betaalmethoden",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_procedure_beschrijving",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Procedure beschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_aanwezig_toelichting",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product aanwezig toelichting",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_titel_decentraal",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product titel decentraal",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_product_valt_onder_toelichting",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product valt onder toelichting",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_uiterste_termijn",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Uiterste termijn",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_vereisten",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Vereisten",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_verwijzing_links",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Verwijzing links",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="localizedproduct_wtd_bij_geen_reactie",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Wtd bij geen reactie",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="product_bevoegde_organisatie",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Bevoegde organisatie",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="product_locaties",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Locaties",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="product_product_aanwezig",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product aanwezig",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="product_product_valt_onder",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Product valt onder",
            ),
        ),
        migrations.AlterField(
            model_name="productfieldconfiguration",
            name="productversie_publicatie_datum",
            field=sdg.core.db.fields.DynamicArrayField(
                base_field=django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=512), size=None
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Publicatie datum",
            ),
        ),
    ]

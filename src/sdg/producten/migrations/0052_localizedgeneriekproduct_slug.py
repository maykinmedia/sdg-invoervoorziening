# Generated by Django 3.2.16 on 2023-04-14 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0051_alter_productversie_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="localizedgeneriekproduct",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="De product title slug van dit gelokaliseerde generieke product",
                max_length=170,
                verbose_name="Product titel slug field",
            ),
        ),
    ]

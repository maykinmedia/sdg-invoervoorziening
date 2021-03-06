# Generated by Django 2.2.24 on 2021-10-29 12:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0008_auto_20211019_1946"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generiekproduct",
            name="verantwoordelijke_organisatie",
            field=models.ForeignKey(
                blank=True,
                help_text="Organisatie verantwoordelijk voor de landelijke informatie",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="generiek_informatie",
                to="core.Overheidsorganisatie",
                verbose_name="verantwoordelijke organisatie",
            ),
        ),
        migrations.AlterField(
            model_name="generiekproduct",
            name="verplicht_product",
            field=models.BooleanField(
                default=False,
                help_text="Geeft aan of decentrale overheden verplicht zijn informatie over dit product te leveren.",
                verbose_name="verplicht product",
            ),
        ),
        migrations.AlterField(
            model_name="productversie",
            name="gemaakt_door",
            field=models.ForeignKey(
                blank=True,
                help_text="De maker van deze productversie.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="productversies",
                to=settings.AUTH_USER_MODEL,
                verbose_name="gemaakt door",
            ),
        ),
        migrations.AlterField(
            model_name="localizedgeneriekproduct",
            name="datum_check",
            field=models.DateTimeField(
                blank=True,
                help_text="De informatie over het product kan worden gewijzigd en gecontroleerd op actualiteit (gecheckt). De Nationale portalen houden bij wanneer de informatie voor het laasts is 'gecheckt'.  Deze datum wordt op het portaal getoond.",
                null=True,
                verbose_name="datum check",
            ),
        ),
    ]

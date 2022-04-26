# Generated by Django 2.2.25 on 2022-04-25 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0019_auto_20220407_1914"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bevoegdeorganisatie",
            name="lokale_overheid",
            field=models.ForeignKey(
                help_text="De verantwoordelijke organisatie horend bij deze bevoegde organisatie.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bevoegde_organisaties",
                to="organisaties.LokaleOverheid",
                verbose_name="lokale overheid",
            ),
        ),
    ]
# Generated by Django 2.2.24 on 2021-09-27 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="contact_naam",
            field=models.CharField(
                help_text="de naam van de verantwoordelijke contactpersoon.",
                max_length=40,
                verbose_name="contact naam",
            ),
        ),
        migrations.AlterField(
            model_name="lokaleoverheid",
            name="ondersteunings_organisatie",
            field=models.ForeignKey(
                help_text="organisatie voor ondersteuning.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ondersteunings",
                to="core.Overheidsorganisatie",
                verbose_name="ondersteunings organisatie",
            ),
        ),
    ]

# Generated by Django 2.2.24 on 2021-10-07 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0005_data_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lokatie",
            name="maandag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="dinsdag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="woensdag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="donderdag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="vrijdag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="zaterdag",
        ),
        migrations.RemoveField(
            model_name="lokatie",
            name="zondag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="dinsdag_tmp",
            new_name="dinsdag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="donderdag_tmp",
            new_name="donderdag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="maandag_tmp",
            new_name="maandag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="vrijdag_tmp",
            new_name="vrijdag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="woensdag_tmp",
            new_name="woensdag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="zaterdag_tmp",
            new_name="zaterdag",
        ),
        migrations.RenameField(
            model_name="lokatie",
            old_name="zondag_tmp",
            new_name="zondag",
        ),
    ]

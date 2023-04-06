# Generated by Django 3.2.16 on 2023-04-05 13:17

from django.db import migrations
from django.db.models import Q


def update_ontvangt_mail_boolean_for_beheerder_and_redacteur(apps, schema_editor):
    roles = apps.get_model("accounts", "Role")
    roles = roles.objects.filter(Q(is_beheerder=True) | Q(is_redacteur=True))
    for role in roles:
        role.ontvangt_mail = True
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0014_role_ontvangt_mail"),
    ]

    operations = [
        migrations.RunPython(
            update_ontvangt_mail_boolean_for_beheerder_and_redacteur,
            migrations.RunPython.noop,
        ),
    ]

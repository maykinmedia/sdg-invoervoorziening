# Generated by Django 2.2.24 on 2021-09-14 14:54

import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone
import sdg.accounts.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "is_hoofdredacteur",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether this user is a root editor (i.e. can edit the reference texts).",
                        verbose_name="hoofdredacteur",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", sdg.accounts.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_beheerder",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether this user is a manager of a specific overheidsorganisatie. ",
                        verbose_name="beheerder",
                    ),
                ),
                (
                    "is_redacteur",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether this is an editor of a specific overheidsorganisatie. ",
                        verbose_name="redacteur",
                    ),
                ),
            ],
            options={
                "verbose_name": "role",
                "verbose_name_plural": "roles",
            },
        ),
    ]

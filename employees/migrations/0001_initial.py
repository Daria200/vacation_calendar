# Generated by Django 4.2.3 on 2023-08-01 14:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "state",
                    models.IntegerField(
                        choices=[
                            (0, "Baden-Württemberg"),
                            (1, "Bavaria (Bayern)"),
                            (2, "Berlin"),
                            (3, "Brandenburg"),
                            (4, "Bremen"),
                            (5, "Hamburg"),
                            (6, "Hesse (Hessen)"),
                            (7, "Lower Saxony (Niedersachsen)"),
                            (
                                8,
                                "Mecklenburg-Western Pomerania (Mecklenburg-Vorpommern)",
                            ),
                            (9, "North Rhine-Westphalia (Nordrhein-Westfalen)"),
                            (10, "Rhineland-Palatinate (Rheinland-Pfalz)"),
                            (11, "Saarland"),
                            (12, "Saxony (Sachsen)"),
                            (13, "Saxony-Anhalt (Sachsen-Anhalt)"),
                            (14, "Schleswig-Holstein"),
                            (15, "Thuringia (Thüringen)"),
                        ]
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Cities",
            },
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_manager", models.BooleanField(default=False)),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="employees.city",
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employees_manager",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

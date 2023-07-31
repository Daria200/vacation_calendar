from django.conf import settings
from django.contrib import admin
from django.db import models


GERMAN_STATES = (
    (0, "Baden-Württemberg"),
    (1, "Bavaria (Bayern)"),
    (2, "Berlin"),
    (3, "Brandenburg"),
    (4, "Bremen"),
    (5, "Hamburg"),
    (6, "Hesse (Hessen)"),
    (7, "Lower Saxony (Niedersachsen)"),
    (8, "Mecklenburg-Western Pomerania (Mecklenburg-Vorpommern)"),
    (9, "North Rhine-Westphalia (Nordrhein-Westfalen)"),
    (10, "Rhineland-Palatinate (Rheinland-Pfalz)"),
    (11, "Saarland"),
    (12, "Saxony (Sachsen)"),
    (13, "Saxony-Anhalt (Sachsen-Anhalt)"),
    (14, "Schleswig-Holstein"),
    (15, "Thuringia (Thüringen)"),
)


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.IntegerField(choices=GERMAN_STATES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employees_manager",
    )

    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

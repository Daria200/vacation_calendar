from django.conf import settings
from django.contrib import admin
from django.db import models


CITY_CHOICES = (
    (0, "Bonn"),
    (1, "Hamburg"),
    (2, "Frankfurt"),
    (3, "Munich"),
)


class Employee(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employees_manager",
    )
    city = models.IntegerField(choices=CITY_CHOICES)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

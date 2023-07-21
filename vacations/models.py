from django.db import models

from employees.models import Employee


class Vacation(models.Model):
    TYPE_CHOICES = ((1, "Vacation"), (2, "Special leave"))

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    # An employee can have half a day off, by default it a full day
    # A full day is 1; a half day is 0.5
    FULL_DAY_CHOICES = (
        (1, "1.0"),
        (0.5, "0.5"),
    )

    full_day = models.DecimalField(
        default=1,
        max_digits=2,
        decimal_places=1,
        choices=FULL_DAY_CHOICES,
    )
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    # Description is needed only if it's a special leave
    # Is disabled when it's a regular vacation
    description = models.CharField(max_length=200, null=True, blank=True)


class PublicHolidays(models.Model):
    CITY_CHOICES = (
        (0, "Bonn"),
        (1, "Hamburg"),
        (2, "Frankfurt"),
        (3, "Munich"),
    )

    city = models.IntegerField(choices=CITY_CHOICES)
    date = models.DateField()

    def __str__(self):
        city_display = dict(self.CITY_CHOICES).get(self.city)
        return f"{city_display} {self.date}"

    class Meta:
        verbose_name_plural = "Public holidays"


# TODO: it does not work
class AvailableDays(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    allotted_days = models.DecimalField(default=30, max_digits=2, decimal_places=1)
    transferred_days = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    year = models.IntegerField()

    class Meta:
        verbose_name_plural = "Available days"

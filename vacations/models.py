import datetime
from django.db import models

from employees.models import Employee, City


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
    date = models.DateField()
    name = models.CharField(max_length=100, null=True, blank=True)
    cities = models.ManyToManyField(City)
    every_year = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Public holidays"


class AvailableDays(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    allotted_days = models.IntegerField(default=30)
    transferred_days = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    year = models.IntegerField(default=datetime.datetime.now().year, editable=True)

    def __str__(self):
        return f"{self.employee} {self.transferred_days}"

    class Meta:
        verbose_name_plural = "Available days"
        unique_together = ["employee", "year"]

class TransferDaysRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()


class DeleteDaysRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
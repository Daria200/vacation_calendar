from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings


# Create your models here.
class Employee(models.Model):
    CITY_CHOICES = (
        (0, 'Bonn'),
        (1, 'Hamburg'),
        (2, 'Frankfurt'),
        (3, 'Munich'),
    )
    user = models.ForeignKey(
       settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    manager = models.ForeignKey(
     settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,related_name='employees_manager'
    )
    city = models.IntegerField(choices=CITY_CHOICES)
    is_manager = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
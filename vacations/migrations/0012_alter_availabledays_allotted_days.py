# Generated by Django 4.2.3 on 2023-08-30 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0011_alter_availabledays_employee_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="availabledays",
            name="allotted_days",
            field=models.DecimalField(decimal_places=1, default=30.0, max_digits=3),
        ),
    ]

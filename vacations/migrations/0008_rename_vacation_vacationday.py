# Generated by Django 4.2.3 on 2023-08-10 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
        ("vacations", "0007_remove_transferdaysrequest_employee_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Vacation",
            new_name="VacationDay",
        ),
    ]
# Generated by Django 4.2.2 on 2023-07-20 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0003_remove_publicholidays_year"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="availabledays",
            options={"verbose_name_plural": "Extra days"},
        ),
        migrations.AlterModelOptions(
            name="publicholidays",
            options={"verbose_name_plural": "Public holidays"},
        ),
    ]
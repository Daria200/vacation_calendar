# Generated by Django 4.2.2 on 2023-07-13 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicholidays",
            name="year",
            field=models.IntegerField(default=2023),
            preserve_default=False,
        ),
    ]
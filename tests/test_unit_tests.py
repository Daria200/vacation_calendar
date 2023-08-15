import datetime
import pytest

from vacations.views import verify_days

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from parameterized import parameterized

from employees.models import City, Employee
from vacations.models import AvailableDays, Request, VacationDay


@pytest.fixture
def employee_user():
    city = City.objects.create(name="Frankfurt", state=6)

    # Create a manager user
    manager_user = User.objects.create_user(
        username="manager",
        password="managerpass",
        email="manager@gmail.com",
    )

    # Create a manager employee instance
    manager_employee = Employee.objects.create(
        user=manager_user,
        city=city,
        is_manager=True,
    )

    # Create a regular employee instance and assign the manager
    user = User.objects.create_user(
        username="testuser",
        password="testpass",
        email="admin@gmail.com",
    )
    employee = Employee.objects.create(
        user=user,
        manager=manager_user,  # Assign the manager instance
        city=city,
        is_manager=False,
    )
    return employee


@pytest.mark.django_db
def test_verify_days(client, employee_user):
    employee = employee_user
    # 7 work days
    start_date = datetime.date(year=2023, month=10, day=6)  # "2023-10-06"
    end_date = datetime.date(year=2023, month=10, day=16)  # "2023-10-16"
    num_days = 11
    current_year = 2023
    full_day = 1.0
    vacation_type = 1
    description = "some"
    days_to_save_in_db = verify_days(
        employee,
        start_date,
        end_date,
        num_days,
        current_year,
        full_day,
        vacation_type,
        description,
    )
    assert len(days_to_save_in_db) == 7

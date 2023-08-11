from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from vacations.models import AvailableDays, VacationDay
from employees.models import Employee, City


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
def test_valid_vacation_request(client, employee_user):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=5.0, year=2023
    )
    available_days.save()

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 30
    )
    client.force_login(employee.user)

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": "2023-08-14",
            "enddate": "2023-08-17",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Some description",
        },
    )

    assert response.status_code == 302
    assert VacationDay.objects.filter(employee=employee).count() == 4


@pytest.mark.django_db
def test_exceeding_available_days(client, employee_user):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=15, transferred_days=0, year=2023
    )

    available_days.save()

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 15
    )
    client.force_login(employee.user)

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": "2023-08-14",
            "enddate": "2023-09-20",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Test vacation request",
        },
    )

    assert response.status_code == 302
    # It did not create new vacation days, because the request exceed the amount of available days
    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 15
    )


@pytest.mark.django_db
def test_request_existing_days(client, employee_user):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=15, transferred_days=0, year=2023
    )

    available_days.save()

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 15
    )
    client.force_login(employee.user)

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": "2023-08-14",
            "enddate": "2023-08-20",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Test vacation request",
        },
    )
    assert VacationDay.objects.filter(employee=employee).count() == 5

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": "2023-08-15",
            "enddate": "2023-08-18",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Test vacation request",
        },
    )
    assert VacationDay.objects.filter(employee=employee).count() == 5

from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from vacations.models import AvailableDays, VacationDay
from employees.models import Employee


@pytest.fixture
def employee_user():
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(user=user)
    return employee


@pytest.mark.django_db
def test_valid_vacation_request(client, employee_user):
    employee = employee_user

    available_days = AvailableDays.objects.create(employee=employee)
    available_days.allotted_days = 30
    available_days.transferred_days = 5
    available_days.save()

    start_date = date.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=5)

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": start_date,
            "enddate": end_date,
            "vacation_type": 1,
            "length": 1.0,
            "description": "Test vacation request",
        },
    )

    assert response.status_code == 302
    assert VacationDay.objects.filter(employee=employee).count() == 5


@pytest.mark.django_db
def test_exceeding_available_days(client, employee_user):
    employee = employee_user

import pytest
from django.contrib.auth.models import User

from employees.models import City, Employee
from vacations.models import AvailableDays, Request, VacationDay
from django.test import Client


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
        is_manager=True,
    )
    return employee


@pytest.fixture
def manager_user():
    # Create a manager user
    user = User.objects.create_user(
        username="manager",
        password="managerpass",
        email="manager@gmail.com",
    )

    return user


@pytest.fixture
def logged_in_manager_client(client, manager_user):
    # Create a client instance
    client = Client()

    # Log in the manager user
    manager_user_data = {
        "username": "manager",
        "password": "managerpass",
    }
    client.login(**manager_user_data)

    return client


@pytest.fixture
def available_days(manager_user):
    # Create and setup AvailableDays instance
    city = City.objects.create(name="Frankfurt", state=6)
    manager_employee = Employee.objects.create(
        user=manager_user,
        city=city,
        is_manager=True,
    )
    available_days = AvailableDays.objects.create(
        employee=manager_employee,
        allotted_days=30,
        transferred_days=5.0,
        year=2023,
    )
    available_days.save()
    return available_days

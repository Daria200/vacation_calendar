import pytest
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
def test_valid_vacation_dec_to_jan_request(client, employee_user):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0.0, year=2023
    )
    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0.0, year=2024
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
            "startdate": "2023-12-25",
            "enddate": "2024-01-05",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Some description",
        },
    )

    assert response.status_code == 302
    assert VacationDay.objects.filter(employee=employee, date__year=2023).count() == 5
    assert VacationDay.objects.filter(employee=employee, date__year=2024).count() == 5


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


@pytest.mark.parametrize(
    "start_date, end_date,status_code, vacation_days_cur_year, allotted_days_last_year, transferred_days_current_year",
    [
        ("2024-01-14", "2024-01-17", 302, 3, 27, 3),
        ("2024-01-14", "2024-02-17", 200, 0, 30, 0),
    ],
)
@pytest.mark.django_db
def test_transfer_request(
    client,
    employee_user,
    start_date,
    end_date,
    status_code,
    vacation_days_cur_year,
    allotted_days_last_year,
    transferred_days_current_year,
):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0.0, year=2023
    )
    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0.0, year=2024
    )

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 30
    )
    client.force_login(employee.user)

    response = client.post(
        reverse("transfer_days_request"),
        {
            "startdate": start_date,
            "enddate": end_date,
            "vacation_type": 2,
            "length": 1.0,
            "description": "Some description",
        },
    )

    assert response.status_code == status_code
    assert (
        VacationDay.objects.filter(employee=employee, date__year=2024).count()
        == vacation_days_cur_year
    )
    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == allotted_days_last_year
    )
    assert (
        AvailableDays.objects.filter(employee=employee, year=2024)
        .first()
        .transferred_days
        == transferred_days_current_year
    )


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
def client_with_manager_logged_in(client, manager_user):
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


@pytest.mark.parametrize(
    "action, expected_status",
    [
        ("approve", 2),
        ("reject", 3),
    ],
)
@pytest.mark.django_db
def test_aprove_reject_vacation_request(
    client_with_manager_logged_in, available_days, action, expected_status
):
    client = client_with_manager_logged_in  # Rename for clarity

    # Create a test vacation request
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

    # Get the created request
    request = Request.objects.first()
    assert request.request_status == 1

    # Perform the action (approve or reject)
    response = client.post(
        reverse("vacation_requests"),
        {
            "selected_requests": [request.id],
            "action": action,
        },
    )
    assert response.status_code == 302

    # Check the updated request status
    assert Request.objects.get(pk=request.id).request_status == expected_status

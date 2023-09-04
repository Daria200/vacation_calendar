import pytest
from django.urls import reverse
from parameterized import parameterized

from vacations.models import AvailableDays, Request, VacationDay, RemoteDay


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
    "start_date, end_date, num_vacation_days_2023, num_vacation_days_2024, status_code",
    [
        ("2023-01-02", "2023-01-15", 10, 0, 302),
        ("2023-08-14", "2023-08-20", 5, 0, 302),
        ("2023-12-25", "2024-01-05", 5, 5, 302),
        ("2023-09-01", "2024-11-20", 0, 0, 302),
    ],
)
@pytest.mark.django_db
def test_vacation_requests(
    client,
    employee_user,
    start_date,
    end_date,
    num_vacation_days_2023,
    num_vacation_days_2024,
    status_code,
):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=20, transferred_days=0, year=2023
    )
    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2024
    )

    available_days.save()

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 20
    )
    assert (
        AvailableDays.objects.filter(employee=employee, year=2024).first().allotted_days
        == 30
    )
    client.force_login(employee.user)

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
    assert response.status_code == status_code
    assert (
        VacationDay.objects.filter(employee=employee, date__year=2023).count()
        == num_vacation_days_2023
    )
    assert (
        VacationDay.objects.filter(employee=employee, date__year=2024).count()
        == num_vacation_days_2024
    )


@pytest.mark.parametrize(
    "start_date, end_date,status_code, vacation_days_cur_year, allotted_days_last_year, transferred_days_current_year",
    [
        ("2024-01-14", "2024-01-17", 302, 3, 30, 0),
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

    AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0.0, year=2023
    )
    AvailableDays.objects.create(
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


@pytest.mark.parametrize(
    "start_date, end_date, request_status",
    [
        ("2023-09-19", "2023-09-21", 1),
    ],
)
@pytest.mark.django_db
def test_cancel_requests(client, employee_user, start_date, end_date, request_status):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2023
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
            "startdate": "2023-09-01",
            "enddate": "2023-09-21",
            "vacation_type": 1,
            "length": 1.0,
            "description": "Test vacation request",
        },
    )
    assert VacationDay.objects.filter(employee=employee, date__year=2023).count() == 15
    # Get the created request
    request = Request.objects.get(request_type=1, employee=employee)
    assert request.request_status == request_status

    # Create a request to cancel days
    response = client.post(
        reverse("cancel_vacation_days"),
        {
            "startdate": start_date,
            "enddate": end_date,
            "description": "Some description",
        },
    )

    assert Request.objects.get(request_type=3, employee=employee).request_status == 1
    assert Request.objects.get(request_type=1, employee=employee).request_status == 1


@pytest.mark.parametrize(
    "start_date, end_date, num_vacation_days_2023",
    [
        ("2023-01-02", "2023-01-15", 5),
        ("2023-08-14", "2023-08-21", 3),
        ("2023-08-01", "2023-09-15", 17),
        ("2023-08-01", "2023-10-02", 22.5),
    ],
)
@pytest.mark.django_db
def test_vacation_requests_0_5_days(
    client,
    employee_user,
    start_date,
    end_date,
    num_vacation_days_2023,
):
    employee = employee_user

    available_days = AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2023
    )

    assert (
        AvailableDays.objects.filter(employee=employee, year=2023).first().allotted_days
        == 30
    )

    client.force_login(employee.user)

    response = client.post(
        reverse("vacation_request"),
        {
            "startdate": start_date,
            "enddate": end_date,
            "vacation_type": 1,
            "length": 0.5,
            "description": "Test vacation request",
        },
    )
    updated_vacation_days = VacationDay.objects.filter(
        employee=employee, date__year=2023
    )
    num_of_days = 0
    for day in updated_vacation_days:
        num_of_days += day.duration
    assert num_of_days == num_vacation_days_2023


@pytest.mark.parametrize(
    "start_date, end_date, num_remote_days",
    [
        ("2024-01-14", "2024-01-17", 3),
        ("2024-01-14", "2024-02-17", 25),
        ("2024-01-05", "2024-02-17", 0),
    ],
)
@pytest.mark.django_db
def test_remote_work_request(
    client, employee_user, start_date, end_date, num_remote_days
):
    employee = employee_user

    AvailableDays.objects.create(
        employee=employee,
        allotted_days=30,
        transferred_days=0.0,
        remote_work_days=30,
        year=2024,
    )

    assert (
        AvailableDays.objects.filter(employee=employee, year=2024)
        .first()
        .remote_work_days
        == 30
    )

    client.force_login(employee.user)

    response = client.post(
        reverse("remote_work_request"),
        {
            "startdate": start_date,
            "enddate": end_date,
            "description": "somedescription",
        },
    )

    assert (
        RemoteDay.objects.filter(employee=employee, date__year=2024).count()
        == num_remote_days
    )

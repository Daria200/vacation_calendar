import pytest
from django.urls import reverse
from parameterized import parameterized
from datetime import timedelta

from vacations.models import AvailableDays, Request, VacationDay


@pytest.mark.parametrize(
    "start_date, end_date, action, expected_status",
    [
        ("2023-08-14", "2023-08-17", "approve", 2),
        ("2023-08-14", "2023-08-17", "reject", 3),
    ],
)
@pytest.mark.django_db
def test_aprove_reject_vacation_request(
    logged_in_manager_client,
    available_days,
    start_date,
    end_date,
    action,
    expected_status,
):
    client = logged_in_manager_client  # Rename for clarity

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
        reverse("requests"),
        {
            "selected_request_id": request.id,
            "action": action,
        },
    )
    assert response.status_code == 302

    # Check the updated request status
    assert Request.objects.get(pk=request.id).request_status == expected_status

    if action == "approve":
        vacation_days_in_db = VacationDay.objects.filter(
            employee=request.employee, date__range=(start_date, end_date)
        )
        for day in vacation_days_in_db:
            assert day.approved == True

    if action == "reject":
        assert (
            len(
                VacationDay.objects.filter(
                    employee=request.employee, date__range=(start_date, end_date)
                )
            )
            == 0
        )


@pytest.mark.parametrize(
    "action, request_status, allotted_days_2023, transfer_days_2024",
    [
        ("approve", 2, 26, 4),
        ("reject", 3, 30, 0),
    ],
)
@pytest.mark.django_db
def test_approve_or_reject_transfer_requests(
    client,
    employee_user,
    action,
    request_status,
    allotted_days_2023,
    transfer_days_2024,
):
    employee = employee_user
    #
    AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2023
    )
    AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2024
    )
    available_days_2023 = AvailableDays.objects.get(employee=employee, year=2023)
    assert available_days_2023.allotted_days == 30

    client.force_login(employee.user)

    # Create a test transfer request
    response = client.post(
        reverse("transfer_days_request"),
        {
            "startdate": "2024-01-02",
            "enddate": "2024-01-05",
            "description": "Some description",
        },
    )
    assert response.status_code == 302

    # Get the created request
    request = Request.objects.get(request_type=2, employee=employee)
    assert request.request_status == 1

    # Perform the action (approve)
    response = client.post(
        reverse("requests"),
        {
            "selected_request_id": request.id,
            "action": action,
        },
    )
    assert response.status_code == 302

    # Check the updated request status
    updated_request = Request.objects.get(pk=request.id)

    assert updated_request.request_status == request_status

    # Check if vacation days are approved
    vacation_days = VacationDay.objects.filter(
        employee=employee, date__range=("2024-01-02", "2024-01-05")
    )
    assert all(vacation_day.approved for vacation_day in vacation_days)

    # Check if available days are updated
    updated_available_days = AvailableDays.objects.get(employee=employee, year=2023)
    assert updated_available_days.allotted_days == allotted_days_2023

    updated_available_days = AvailableDays.objects.get(employee=employee, year=2024)
    assert updated_available_days.transferred_days == transfer_days_2024

    # Perform the action (reject)
    response = client.post(
        reverse("requests"),
        {
            "selected_request_id": request.id,
            "action": "reject",
        },
    )
    assert response.status_code == 302

    # Check the updated request status
    updated_request = Request.objects.get(pk=request.id)
    assert updated_request.request_status == 3

    # Check if vacation days are deleted
    assert not VacationDay.objects.filter(
        employee=employee, date__range=("2024-01-02", "2024-01-05")
    ).exists()

    # Check if available days are not further updated after rejection
    updated_available_days = AvailableDays.objects.get(employee=employee, year=2023)


@pytest.mark.parametrize(
    "request_status_vacation, action",
    [
        (1, "approve"),
        (1, "reject"),
    ],
)
@pytest.mark.django_db
def test_approve_or_reject_cancel_requests(
    client,
    employee_user,
    request_status_vacation,
    action,
):
    employee = employee_user
    #
    AvailableDays.objects.create(
        employee=employee, allotted_days=30, transferred_days=0, year=2023
    )
    available_days_2023 = AvailableDays.objects.get(employee=employee, year=2023)
    assert available_days_2023.allotted_days == 30

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
    assert request.request_status == 1

    # Create a request to cancel days
    response = client.post(
        reverse("cancel_vacation_days"),
        {
            "startdate": "2023-09-10",
            "enddate": "2023-09-21",
            "description": "Some description",
        },
    )

    requests = Request.objects.filter(employee=employee)
    assert requests[0].request_status == request_status_vacation
    assert requests[1].request_status == request_status_vacation

    # Perform the action (reject)
    response = client.post(
        reverse("requests"),
        {
            "selected_request_id": 2,
            "action": action,
        },
    )

    if action == "approve":
        assert (
            VacationDay.objects.filter(employee=employee, date__year=2023).count() == 6
        )
        request = Request.objects.get(request_type=3, employee=employee)
        assert request.request_status == 2
        assert not VacationDay.objects.filter(
            employee=employee, date__range=("2023-09-10", "2023-09-21")
        ).exists()

    elif action == "reject":
        assert (
            VacationDay.objects.filter(employee=employee, date__year=2023).count() == 15
        )
        request = Request.objects.get(request_type=3, employee=employee)
        assert request.request_status == 3
        assert VacationDay.objects.filter(
            employee=employee, date__range=("2023-09-10", "2023-09-21")
        ).exists()


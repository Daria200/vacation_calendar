import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F, Q, Sum
from django.shortcuts import redirect, render

from employees.models import City, Employee
from vacations.models import AvailableDays, Request, VacationDay


def is_manager(user):
    return user.is_authenticated and user.employee.is_manager


@user_passes_test(is_manager)
@login_required
def requests(request):
    all_requests = Request.objects.filter(request_status=1)
    context = {"all_requests": all_requests}
    return render(request, "manager_view/requests.html", context)


@user_passes_test(is_manager)
@login_required
def vacation_requests(request):
    vacation_requests = Request.objects.filter(request_type=1, request_status=1)
    context = {"vacation_requests": vacation_requests}

    if request.method == "POST":
        selected_request_id = request.POST["selected_request_id"]
        action = request.POST["action"]

        vacation_request_to_approve_or_reject = Request.objects.get(
            pk=selected_request_id
        )
        employee = vacation_request_to_approve_or_reject.employee
        start_date = vacation_request_to_approve_or_reject.start_date
        end_date = vacation_request_to_approve_or_reject.end_date
        vacation_days_to_approve_or_reject = VacationDay.objects.filter(
            employee=employee,
            date__range=(start_date, end_date),
        )

        if action == "approve":
            # approve vacation days in db (VacationDay)
            # update the request (Request)
            with transaction.atomic():
                vacation_request_to_approve_or_reject.request_status = 2
                vacation_request_to_approve_or_reject.save()
                vacation_days_to_approve_or_reject.update(approved=True)
                messages.success(request, f"The request has been approved")

        elif action == "reject":
            # delete vacation days in db (VacationDay)
            # set the request to rejected (Request)
            with transaction.atomic():
                vacation_request_to_approve_or_reject.request_status = 3
                vacation_request_to_approve_or_reject.save()
                vacation_days_to_approve_or_reject.delete()
                messages.success(request, f"The request has been rejected")

        return redirect("vacation_requests")
    # employees = employees.select_related("user")
    return render(request, "manager_view/vacation_days_requests.html", context)


@user_passes_test(is_manager)
@login_required
def transfer_days_requests(request):
    # If a request is approved, set the status to approved and create vacation days,
    # remove days from this year and days to the next year
    # If a request is rejected, set the status to rejected

    transfer_requests = Request.objects.filter(request_type=2, request_status=1)
    context = {"transfer_requests": transfer_requests}

    if request.method == "POST":
        selected_request_id = request.POST["selected_request_id"]
        action = request.POST["action"]

        transfer_request_to_approve_or_reject = Request.objects.get(
            pk=selected_request_id
        )
        employee = transfer_request_to_approve_or_reject.employee
        start_date = transfer_request_to_approve_or_reject.start_date
        end_date = transfer_request_to_approve_or_reject.end_date

        vacation_days_to_approve_or_reject = VacationDay.objects.filter(
            employee=employee,
            date__range=(start_date, end_date),
        )
        num_of_days = len(vacation_days_to_approve_or_reject)

        if action == "approve":
            start_year = start_date.year
            available_days_instance_next_year = AvailableDays.objects.get(
                employee=employee,
                year=start_year,
            )
            available_days_this_year = AvailableDays.objects.get(
                employee=employee, year=start_year - 1
            )
            # approve vacation days in db (VacationDay)
            # update the request (Request)
            # subtract days from allotted days this year
            # add transferred days next year
            with transaction.atomic():
                transfer_request_to_approve_or_reject.request_status = 2
                transfer_request_to_approve_or_reject.save()
                vacation_days_to_approve_or_reject.update(approved=True)
                available_days_instance_next_year.transferred_days = (
                    F("transferred_days") + num_of_days
                )
                available_days_instance_next_year.save()
                available_days_this_year.allotted_days = (
                    F("allotted_days") - num_of_days
                )
                available_days_this_year.save()
                messages.success(request, f"The request has been approved")

        elif action == "reject":
            # delete vacation days in db (VacationDay)
            # set the request to rejected (Request)
            with transaction.atomic():
                transfer_request_to_approve_or_reject.request_status = 3
                transfer_request_to_approve_or_reject.save()
                vacation_days_to_approve_or_reject.delete()
                messages.success(request, f"The request has been rejected")

        return redirect("transfer_days_requests")
    employees = employees.select_related("user")
    return render(request, "manager_view/transfer_days_requests.html", context)


@user_passes_test(is_manager)
@login_required
def cancel_days_requests(request):
    cancel_requests = Request.objects.filter(request_type=3, request_status=1)
    context = {"cancel_requests": cancel_requests}
    if request.method == "POST":
        selected_request_id = request.POST["selected_request_id"]
        action = request.POST["action"]

        cancel_request_to_approve_or_reject = Request.objects.get(
            pk=selected_request_id
        )
        employee = cancel_request_to_approve_or_reject.employee
        start_date = cancel_request_to_approve_or_reject.start_date
        end_date = cancel_request_to_approve_or_reject.end_date

        vacation_days_to_approve_or_reject = VacationDay.objects.filter(
            employee=employee,
            date__range=(start_date, end_date),
        )

        if action == "approve":
            with transaction.atomic():
                # Set the request status to apptove
                # Delete the days from the DB
                vacation_days_to_approve_or_reject.delete()
                cancel_request_to_approve_or_reject.request_status = 2
                cancel_request_to_approve_or_reject.save()
                messages.success(request, f"The request has been approved")

        elif action == "reject":
            # Set the request status to rejected
            with transaction.atomic():
                cancel_request_to_approve_or_reject.request_status = 3
                cancel_request_to_approve_or_reject.save()
                messages.success(request, f"The request has been rejected")
    employees = employees.select_related("user")
    return render(request, "manager_view/delete_days_requests.html", context)


@user_passes_test(is_manager)
@login_required
def hr_view(request):
    managers = Employee.objects.filter(is_manager=True)
    cities = City.objects.all()

    employee_name = request.GET.get("employee_name")
    year = request.GET.get("year", datetime.date.today().year)
    manager_id = request.GET.get("manager")
    city_id = request.GET.get("city")

    employees = Employee.objects.all()

    if employee_name:
        employees = employees.filter(
            Q(user__first_name__icontains=employee_name)
            | Q(user__last_name__icontains=employee_name)
        )
    if manager_id:
        employees = employees.filter(manager_id=manager_id)
    if city_id:
        employees = employees.filter(city_id=city_id)

    # Get vacation days
    vacation_days = VacationDay.objects.filter(date__year=year, employee__in=employees)
    employee_id_to_vacation_days = {}
    employee_id_to_approved_days = {}

    for vacation_day in vacation_days:
        if vacation_day.employee.id not in employee_id_to_vacation_days:
            employee_id_to_vacation_days[vacation_day.employee.id] = 0
            employee_id_to_approved_days[vacation_day.employee.id] = 0
        employee_id_to_vacation_days[vacation_day.employee.id] += vacation_day.full_day
        if vacation_day.approved:
            employee_id_to_approved_days[
                vacation_day.employee.id
            ] += vacation_day.full_day

    # Get available days

    for employee in employees:
        setattr(
            employee,
            "total_vacation_days",
            employee_id_to_vacation_days.get(employee.id, 0),
        )
        setattr(
            employee,
            "total_approved_days",
            employee_id_to_approved_days.get(employee.id, 0),
        )
    employees = employees.select_related("user")
    context = {
        "managers": managers,
        "cities": cities,
        "employees": employees,
        "year": year,
    }
    return render(request, "manager_view/hr_view.html", context)


def manager_view_monthly(request):
    return render(request, "manager_view/monthly.html")


def manager_view_total(request):
    return render(request, "manager_view/total.html")

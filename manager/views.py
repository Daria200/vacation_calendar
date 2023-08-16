from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from employees.models import Employee
from vacations.models import Request, VacationDay
from vacations.views import verify_days


@login_required
def vacation_requests(request):
    vacation_requests = Request.objects.filter(request_type=1, request_status=1)
    context = {"vacation_requests": vacation_requests}

    if request.method == "POST":
        selected_request_ids = request.POST.getlist("selected_requests")
        action = request.POST.get("action")
        requests_to_update = Request.objects.filter(pk__in=selected_request_ids)

        if action == "approve":
            # Update request status and corresponding vacation days
            with transaction.atomic():
                requests_to_update.update(request_status=2)

                # Update vacation days for each approved request
                for request in requests_to_update:
                    start_date = request.start_date
                    end_date = request.end_date
                    vacation_days = VacationDay.objects.filter(
                        employee=request.employee, date__range=(start_date, end_date)
                    )
                    # TODO: does it work?
                    vacation_days.update(approved=True)
        elif action == "reject":
            # Delete vacation days and update request status
            with transaction.atomic():
                for request in requests_to_update:
                    start_date = request.start_date
                    end_date = request.end_date
                    vacation_days_to_delete = VacationDay.objects.filter(
                        employee=request.employee, date__range=(start_date, end_date)
                    )
                    vacation_days_to_delete.delete()
                    request.request_status = 3
                    request.save()

        return redirect("vacation_requests")

    return render(request, "manager_view/vacation_days_requests.html", context)


@login_required
def transfer_days_requests(request):
    # If a request is approved, set the status to approved and create vacation days,
    # remove days from this year and days to the next year
    # If a request is rejected, set the status to rejected

    transfer_requests = Request.objects.filter(request_type=2, request_status=1)
    context = {"transfer_requests": transfer_requests}

    if request.method == "POST":
        selected_request_ids = request.POST.getlist("selected_requests")
        action = request.POST.get("action")

        print(action)
        requests_to_approve = Request.objects.filter(
            request_type=2, request_status=1, pk__in=selected_request_ids
        )

        employees_requested_transfer = set()
        for request in requests_to_approve:
            employees_requested_transfer.add(request.employee)

        for employee in employees_requested_transfer:
            employee_requests = requests_to_approve.filter(employee=employee)
            total_days_requested = 0
            for request in employee_requests:
                num_days = (request.end_date - request.start_date).days + 1
                work_days = verify_days(
                    employee,
                    request.start_date,
                    num_days,
                    request.start_date.year,
                )
                total_days_requested += len(work_days)
            print(employee, total_days_requested)

        if action == "approve":
            with transaction.atomic():
                requests_to_approve.update(request_status=2)

                # Update vacation days for each approved request
                for request in requests_to_approve:
                    start_date = request.start_date
                    end_date = request.end_date
                    vacation_days = VacationDay.objects.filter(
                        employee=request.employee, date__range=(start_date, end_date)
                    )
                    vacation_days.update(approved=True)
        elif action == "reject":
            # Delete vacation days and update request status
            with transaction.atomic():
                for request in requests_to_update:
                    start_date = request.start_date
                    end_date = request.end_date
                    vacation_days_to_delete = VacationDay.objects.filter(
                        employee=request.employee, date__range=(start_date, end_date)
                    )
                    vacation_days_to_delete.delete()
                    request.request_status = 3
                    request.save()

        return redirect("transfer_days_requests")
    return render(request, "manager_view/transfer_days_requests.html", context)


def cancel_days_requests(request):
    return render(request, "manager_view/delete_days_requests.html")


def hr_view(request):
    return render(request, "manager_view/hr_view.html")


def manager_view_monthly(request):
    return render(request, "manager_view/monthly.html")


def manager_view_total(request):
    return render(request, "manager_view/total.html")

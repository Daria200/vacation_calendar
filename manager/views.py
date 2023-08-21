from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

from vacations.models import AvailableDays, Request, VacationDay
from vacations.views import verify_days


@login_required
def vacation_requests(request):
    vacation_requests = Request.objects.filter(request_type=1, request_status=1)
    context = {"vacation_requests": vacation_requests}

    if request.method == "POST":
        print(request.POST)
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
                messages.successr(request, f"The request has been approved")

        elif action == "reject":
            # delete vacation days in db (VacationDay)
            # set the request to rejected (Request)
            with transaction.atomic():
                vacation_request_to_approve_or_reject.request_status = 3
                vacation_request_to_approve_or_reject.save()
                vacation_days_to_approve_or_reject.delete()
                messages.successr(request, f"The request has been rejected")

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

        requests_to_update = Request.objects.filter(
            request_type=2, request_status=1, pk__in=selected_request_ids
        ).select_related("employee")

        for request in requests_to_update:
            start_date = request.start_date
            end_date = request.end_date
            vacation_days_to_update_or_delete = VacationDay.objects.filter(
                employee=request.employee, date__range=(start_date, end_date)
            )

        combined_queryset_vacation_days = VacationDay.objects.none()

        for request in requests_to_update:
            start_date = request.start_date
            end_date = request.end_date
            vacation_days_to_update_or_delete.append(
                VacationDay.objects.filter(
                    employee=request.employee, date__range=(start_date, end_date)
                )
            )

        # Combine all the individual querysets into a single combined_queryset
        for vacation_days_queryset in vacation_days_to_update_or_delete:
            combined_queryset_vacation_days |= vacation_days_queryset

        if action == "approve":
            available_days_instances = []
            previous_year_available_days_instances = []
            for request in requests_to_update:
                num_days = (end_date - start_date).days + 1
                start_year = start_date.year
                employee = request.employee
                num_of_work_days = verify_days(
                    employee, start_date, num_days, start_year
                )

                available_days_instance = AvailableDays.objects.get(
                    employee=employee,
                    year=start_year,
                )
                available_days_instances.append(available_days_instance)

                # Update allotted days for the previous year
                previous_year = start_year - 1
                previous_year_available_days = AvailableDays.objects.get(
                    employee=employee, year=previous_year
                )
                previous_year_available_days_instances.append(
                    previous_year_available_days
                )

            with transaction.atomic():
                requests_to_update.update(request_status=2)
                available_days_instance.transferred_days = F("transferred_days") + len(
                    num_of_work_days
                )
                available_days_instance.save()
                previous_year_available_days.allotted_days = F("allotted_days") - len(
                    num_of_work_days
                )
                previous_year_available_days.save()
                vacation_days_to_update_or_delete.update(approved=True)

        elif action == "reject":
            # Delete vacation days and update request status
            with transaction.atomic():
                combined_queryset_vacation_days.delete()
                requests_to_update.request_status = 3

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

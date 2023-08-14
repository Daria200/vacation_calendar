from django.db import transaction
from django.shortcuts import redirect, render

from vacations.models import Request, VacationDay


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


def transfer_days_requests(request):
    return render(request, "manager_view/transfer_days_requests.html")


def cancel_days_requests(request):
    return render(request, "manager_view/delete_days_requests.html")


def hr_view(request):
    return render(request, "manager_view/hr_view.html")


def manager_view_monthly(request):
    return render(request, "manager_view/monthly.html")


def manager_view_total(request):
    return render(request, "manager_view/total.html")

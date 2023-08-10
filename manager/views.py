from django.shortcuts import render
from vacations.models import Request


def vacation_requests(request):
    vacation_requests = Request.objects.filter(request_type=1)
    context = {"vacation_requests": vacation_requests}
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

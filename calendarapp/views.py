from django.shortcuts import render
from django.http import HttpResponse


# Disply employee's own dashboard
def index(request):
    return render(request, "dashboard.html")


# Managers can view calendars of the employees
def employee_calendar(request):
    return render(request, "employee_calendar.html")

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "dashboard.html")


def employee(request):
    return render(render, "employee.html")

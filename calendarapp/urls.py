from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar, name="calendar"),
    path("employee_calendar", views.employee_calendar, name="employee_calendar"),
    path("dashboard", views.dashboard, name="dashboard"),
]

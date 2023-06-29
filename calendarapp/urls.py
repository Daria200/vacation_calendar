from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("employee_calendar", views.employee_calendar, name="employee_calendar"),
    path("events", views.events, name="events"),
]

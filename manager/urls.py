from django.urls import path

from . import views

urlpatterns = [
    path("requests", views.requests, name="requests"),
    path("vacation_requests", views.vacation_requests, name="vacation_requests"),
    path(
        "transfer_days_requests",
        views.transfer_days_requests,
        name="transfer_days_requests",
    ),
    path(
        "cancel_days_requests", views.cancel_days_requests, name="cancel_days_requests"
    ),
    path("hr_view", views.hr_view, name="hr_view"),
    path(
        "manager_view_monthly", views.manager_view_monthly, name="manager_view_monthly"
    ),
    path("manager_view_total", views.manager_view_total, name="manager_view_total"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("requests", views.requests, name="requests"),
    path("hr_view", views.hr_view, name="hr_view"),
    path(
        "manager_view_monthly", views.manager_view_monthly, name="manager_view_monthly"
    ),
    path("manager_view_total", views.manager_view_total, name="manager_view_total"),
]

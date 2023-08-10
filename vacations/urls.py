from django.urls import path

from . import views

urlpatterns = [
    path("vacation_request", views.vacation_request, name="vacation_request"),
    path("transfer_days_request", views.transfer_days_request, name="transfer_days_request"),
    path("cancel_vacation_days", views.cancel_vacation_days, name="cancel_vacation_days"),
]

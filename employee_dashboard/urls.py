from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar, name="calendar"),
    path("dashboard", views.dashboard, name="dashboard"),
]

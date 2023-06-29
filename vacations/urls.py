from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_event, name="add_event"),
]

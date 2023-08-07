from django.shortcuts import render
from employees.models import Employee, City


# Display employee's calendar
# Click a cell and add a request
# add a short list on the left side
def calendar(request):
    return render(request, "calendar.html")


# TODO:redo
def employee_calendar(request):
    managers = Employee.objects.filter(is_manager=True)
    cities = City.objects.all()
    context={"managers":managers, 'cities':cities}
    return render(request, "employee_calendar.html", context)


# Employees can see their progress and which days they have taken
# they will see how many days are left
def dashboard(request):
    return render(request, "dashboard.html")

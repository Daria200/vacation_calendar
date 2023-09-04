from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from employees.models import City, Employee
from vacations.models import Request, VacationDay, AvailableDays


# Display employee's calendar
# Click a cell and add a request
# add a short list on the left side
def calendar(request):
    return render(request, "employee_view/calendar.html")


# TODO:redo
def employee_calendar(request):
    managers = Employee.objects.filter(is_manager=True)
    cities = City.objects.all()
    context = {"managers": managers, "cities": cities}
    return render(request, "employee_calendar.html", context)


# Employees can see their progress and which days they have taken
# they will see how many days are left
@login_required
def dashboard(request):
    STATUS_LABELS = {
        1: "Pending",
        2: "Approved",
        3: "Rejected",
    }

    TYPE_LABELS = {
        1: "Vacation",
        2: "Transfer",
        3: "Cancel",
        4: 'Remote Work'
    }

    user_id = request.user.id
    employee = Employee.objects.get(user_id=user_id)
    years = AvailableDays.objects.filter(employee=employee).values_list('year', flat=True).distinct()
    current_year = date.today().year

    if request.method == "POST":
        print(request.POST)
        current_year =int(request.POST["year"])

    all_requests_this_year = Request.objects.filter(
        employee=employee, start_date__year=current_year
    )
    transfer_requests_next_year = Request.objects.filter(
        employee=employee, start_date__year=current_year + 1, request_type=2
    )
    # if not transfer_requests_next_year.exists():
    #     transfer_requests_next_year = None
    
    if transfer_requests_next_year:
        # Combine querysets using the OR operator
        all_requests = all_requests_this_year | transfer_requests_next_year
    else:
        all_requests = all_requests_this_year
    vacation_days_saved_in_db_this_year = VacationDay.objects.filter(
            employee=employee, date__year=current_year
        )
    

    num_of_vac_days = len(vacation_days_saved_in_db_this_year)
    available_days_instance = AvailableDays.objects.get(
        employee=employee, year=current_year
    )
    num_of_alloted_days = available_days_instance.allotted_days
    num_of_transferred_days = available_days_instance.transferred_days
    all_available_days = num_of_alloted_days + num_of_transferred_days
    days_left_this_year = all_available_days - num_of_vac_days
    usage = round((num_of_vac_days / all_available_days) * 100)

    context = {
        "all_requests": all_requests,
        "num_of_vac_days": num_of_vac_days,
        "all_available_days": all_available_days,
        "num_of_alloted_days": num_of_alloted_days,
        "num_of_transferred_days": num_of_transferred_days,
        "days_left_this_year": days_left_this_year,
        "usage": usage,
        "years": years,
        "current_year": current_year,
    }
    return render(request, "employee_view/dashboard.html", context)


from django import template

register = template.Library()

@register.filter
def dict_lookup(dictionary, key):
    return dictionary.get(key, key)
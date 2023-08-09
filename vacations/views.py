from datetime import timedelta, date
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.models import Employee
from .models import Vacation, PublicHolidays, Request


# Create your views here.
@login_required
def vacation_request(request):
    # Get the days
    # exclude saturdays and sundays
    # return error, if the days are already in the database
    # exclude public holidays this of this year
    # exclude public holidays that happen every year
    # check if the employee does not exceed the available days
    # Get public holidays, saved_days
    # Calculate the amount of days requested (not weekend, not public holiday, not in the DB)

    # DO NOT FORGET

    # Reject if the sum of requested + saved days exceed available days (sum allotted and transferred)
    # Save in bulk

    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)
        employee_id = employee.id

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        vacation_type = request.POST["vacation_type"]
        full_day = float(request.POST["length"])
        description = request.POST.get("description", None)

        # Convert the date strings to datetime objects
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()

        # Calculate the number of days between the start and end dates
        num_days = (end_date - start_date).days + 1

        # Get Public holidays:
        # Need the city and the year
        employee_city = request.user.employee.city
        current_year = date.today().year
        # Get public holidays for this year
        public_holidays_this_year = PublicHolidays.objects.filter(
            cities=employee_city,
            date__year=current_year,
        )
        # Get public holidays that happen every year
        public_holidays_every_year = PublicHolidays.objects.filter(
            cities=employee_city,
            every_year=True,
        )

        public_holidays_set = set()

        for holiday in public_holidays_this_year:
            public_holidays_set.add(holiday.date)

        # Add public holidays that happen every year to the set, adjusting the year to the current year
        for holiday in public_holidays_every_year:
            current_date = date(current_year, holiday.date.month, holiday.date.day)
            public_holidays_set.add(current_date)

        # Saved days in the database
        vacation_days_saved_in_db = Vacation.objects.filter(employee=employee)

        # Create a list of Vacation instances to save in bulk
        vacation_instances = []

        # Exclude weekends (Saturday and Sunday)
        # Loop through each day between the start and end dates
        for i in range(num_days):
            current_date = start_date + timedelta(days=i)

            # Exclude weekends (Saturday and Sunday) and public holidays
            if (
                current_date.weekday() not in [5, 6]
                and current_date not in public_holidays_set
            ):
                # Check if the record is in the DB
                if vacation_days_saved_in_db.filter(date=current_date).exists():
                    messages.error(request, f"You already requested {current_date}")
                    break

                # Create a Vacation instance and save it to the database
                else:
                    vacation_instances.append(
                        Vacation(
                            employee=employee,
                            date=current_date,
                            full_day=full_day,
                            approved=False,
                            type=vacation_type,
                            description=description,
                        )
                    )

        # Use bulk_create to save the instances in bulk

        if len(vacation_instances) > 0:
            Vacation.objects.bulk_create(vacation_instances)
            messages.success(
                request, f"You requested {len(vacation_instances)} days"
            )
            vacation_request = Request.objects.create(
                employee=employee,
                start_date=startdate,
                end_date=enddate,
                description=description,
                request_type=1,
            )
            vacation_request.save()
        return redirect("vacation_request")

    return render(request, "employee_view/vacation_request.html")


def transfer_days_request(request):
    return render(request, "employee_view/transfer_days_request.html")


def cancel_vacation_days(request):
    return render(request, "employee_view/cancel_vacation_days.html")

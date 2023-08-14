import datetime
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from employees.models import Employee

from .models import AvailableDays, PublicHolidays, Request, VacationDay


@login_required
def vacation_request(request):
    # exclude saturdays and sundays, public holidays, save it in the database
    # return error if:
    #   the days are already in the database
    #   the sum of requested + saved days exceed available days

    # TODO: edge case
    # A vacation can start in december and end in januar

    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

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
        current_year = start_date.year
        # Get public holidays for this year
        public_holidays_this_year = PublicHolidays.objects.filter(
            cities=employee_city,
            date__year=current_year,
            every_year=False,
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

        # Get saved days in the database
        vacation_days_saved_in_db = VacationDay.objects.filter(
            employee=employee, date__year=current_year
        )
        vacation_days_saved_in_db_list = [
            day.date.strftime("%Y-%m-%d") for day in vacation_days_saved_in_db
        ]

        # Get number of available days for the employee
        available_days_instance = AvailableDays.objects.get(
            employee=employee, year=current_year
        )
        # Calculate total available days (allotted+transferred)
        total_available_days = (
            available_days_instance.allotted_days
            + available_days_instance.transferred_days
        )
        # Create a list of Vacation instances to save in bulk
        vacation_instances = []

        # Loop through each day between the start and end dates
        for i in range(num_days):
            current_date = start_date + timedelta(days=i)

            # Exclude weekends (Saturday and Sunday) and public holidays
            if (
                current_date.weekday() not in [5, 6]
                and current_date not in public_holidays_set
            ):
                # Check if the record is in the DB
                if current_date.strftime("%Y-%m-%d") in vacation_days_saved_in_db_list:
                    messages.error(request, f"You already requested {current_date}")
                    break

                # Create a Vacation instance and prepare to save it to the database
                vacation_instances.append(
                    VacationDay(
                        employee=employee,
                        date=current_date,
                        full_day=full_day,
                        approved=False,
                        type=vacation_type,
                        description=description,
                    )
                )

        if len(vacation_instances) > 0:
            # Check if the employee does not exceed the available days
            if (
                len(vacation_instances) + len(vacation_days_saved_in_db)
                > total_available_days
            ):
                messages.error(
                    request,
                    f"You requested {len(vacation_instances)} days, but you have only {int(total_available_days) - len(vacation_days_saved_in_db)} available days for {current_year}",
                )
            else:
                with transaction.atomic():
                    VacationDay.objects.bulk_create(vacation_instances)
                    Request.objects.create(
                        employee=employee,
                        start_date=startdate,
                        end_date=enddate,
                        description=description,
                        request_type=1,
                    )
                messages.success(
                    request, f"You requested {len(vacation_instances)} days"
                )
        return redirect("vacation_request")

    return render(request, "employee_view/vacation_request.html")


def transfer_days_request(request):
    return render(request, "employee_view/transfer_days_request.html")


def cancel_vacation_days(request):
    return render(request, "employee_view/cancel_vacation_days.html")

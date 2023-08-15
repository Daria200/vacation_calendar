import datetime
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

from employees.models import Employee

from .models import AvailableDays, PublicHolidays, Request, VacationDay


def verify_days(
    employee,
    start_date,
    end_date,
    num_days,
    current_year,
    full_day,
    type,
    description,
):
    """_summary_

    Args:
        employee (_type_): _description_
        employee_city (_type_): _description_
        start_date (_type_): _description_
        end_date (_type_): _description_
        num_days (_type_): _description_
        current_year (_type_): _description_
        full_day (_type_): _description_
        type (_type_): _description_
        description (_type_): _description_


    Using start and end date, exclude weekends and public holidays
    Return days to save

    Returns:
        list of vacation_instances
    """

    # Get public holidays for this year
    public_holidays_this_year = PublicHolidays.objects.filter(
        cities=employee.city,
        date__year=current_year,
        every_year=False,
    )
    # Get public holidays that happen every year
    public_holidays_every_year = PublicHolidays.objects.filter(
        cities=employee.city,
        every_year=True,
    )

    public_holidays_set = set()

    for holiday in public_holidays_this_year:
        public_holidays_set.add(holiday.date)

    # Add public holidays that happen every year to the set, adjusting the year to the current year
    for holiday in public_holidays_every_year:
        current_date = date(current_year, holiday.date.month, holiday.date.day)
        public_holidays_set.add(current_date)

    # Create a list of Vacation instances to save in bulk
    vacation_instances = []

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)

        # Exclude weekends (Saturday and Sunday) and public holidays
        if (
            current_date.weekday() not in [5, 6]
            and current_date not in public_holidays_set
        ):
            # Create a Vacation instance and prepare to save it to the database
            vacation_instances.append(
                VacationDay(
                    employee=employee,
                    date=current_date,
                    full_day=full_day,
                    approved=False,
                    type=type,
                    description=description,
                )
            )
    return vacation_instances


@login_required
def vacation_request(request):
    # exclude saturdays and sundays, public holidays, save it in the database
    # return error if:
    #   the days are already in the database
    #   the sum of requested + saved days exceed available days

    # TODO: edge case
    # A vacation can start in december and end in januar
    # An employee can request 0.5 day

    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        vacation_type = request.POST["vacation_type"]
        full_day = float(request.POST["length"])
        description = request.POST.get("description")

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        current_year = start_date.year
        vacation_days_saved_in_db = VacationDay.objects.filter(
            employee=employee, date__year=current_year
        )
        vacation_days_saved_in_db_list = [
            day.date.strftime("%Y-%m-%d") for day in vacation_days_saved_in_db
        ]
        # Check if the record is in the DB
        num_days = (end_date - start_date).days + 1
        for i in range(num_days):
            current_date = start_date + timedelta(days=i)
            if current_date.strftime("%Y-%m-%d") in vacation_days_saved_in_db_list:
                messages.error(request, f"You already requested {current_date}")
                return redirect("vacation_request")

        days_to_save_in_db = verify_days(
            employee,
            start_date,
            end_date,
            num_days,
            current_year,
            full_day,
            vacation_type,
            description,
        )

        # Check if the employee does not exceed the available days
        # Get number of available days for the employee
        available_days_instance = AvailableDays.objects.get(
            employee=employee, year=current_year
        )
        # Calculate total available days (allotted+transferred)
        total_available_days = (
            available_days_instance.allotted_days
            + available_days_instance.transferred_days
        )

        if len(days_to_save_in_db) > int(total_available_days) - len(
            vacation_days_saved_in_db
        ):
            messages.error(
                request,
                f"You requested {len(days_to_save_in_db)} days, but you have only {int(total_available_days) - len(vacation_days_saved_in_db)} available days for {current_year}",
            )
        else:
            with transaction.atomic():
                VacationDay.objects.bulk_create(days_to_save_in_db)
                Request.objects.create(
                    employee=employee,
                    start_date=startdate,
                    end_date=enddate,
                    description=description,
                    request_type=1,
                )
            messages.success(request, f"You requested {len(days_to_save_in_db)} days")
        return redirect("vacation_request")

    return render(request, "employee_view/vacation_request.html")


# check that the dates are in the first three months of the year
# remove alloted days from previuos year, add transferred days to this year after approved
@login_required
def transfer_days_request(request):
    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        vacation_type = 1
        full_day = "1.0"
        description = request.POST.get("description")

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        current_year = start_date.year
        vacation_days_saved_in_db = VacationDay.objects.filter(
            employee=employee, date__year=current_year
        )
        vacation_days_saved_in_db_list = [
            day.date.strftime("%Y-%m-%d") for day in vacation_days_saved_in_db
        ]

        # Calculate the number of days between the start and end dates
        num_days = (end_date - start_date).days + 1
        for i in range(num_days):
            current_date = start_date + timedelta(days=i)
            # Check if the record is in the DB
            if current_date.strftime("%Y-%m-%d") in vacation_days_saved_in_db_list:
                messages.error(request, f"You already requested {current_date}")
                return redirect("transfer_days_request")
        days_to_save_in_db = verify_days(
            employee,
            start_date,
            end_date,
            num_days,
            current_year,
            full_day,
            vacation_type,
            description,
        )
        available_days_instance = AvailableDays.objects.get(
            employee=employee,
            year=current_year,
        )
        number_of_transferred_days = available_days_instance.transferred_days
        all_transferred = number_of_transferred_days + len(days_to_save_in_db)
        if len(days_to_save_in_db) > 10 or all_transferred > 10:
            messages.error(
                request,
                f"You can request to transfer up to 10 days.\n"
                f"You request {len(days_to_save_in_db)} days.\n"
                f"You have {number_of_transferred_days} transferred days for the next year",
            )
        else:
            with transaction.atomic():
                # create vacation days and the request
                VacationDay.objects.bulk_create(days_to_save_in_db)
                Request.objects.create(
                    employee=employee,
                    start_date=startdate,
                    end_date=enddate,
                    description=description,
                    request_type=2,
                )
                # Update available days for the current year
                available_days_instance.transferred_days = F("transferred_days") + len(
                    days_to_save_in_db
                )
                available_days_instance.save()

                # Update transferred days for the previous year
                previous_year = current_year - 1
                previous_year_available_days = AvailableDays.objects.get(
                    employee=employee, year=previous_year
                )
                previous_year_available_days.allotted_days = F("allotted_days") - len(
                    days_to_save_in_db
                )
                previous_year_available_days.save()
            messages.success(
                request,
                f"You requested {len(days_to_save_in_db)} days to transfer to {current_year} year",
            )
            return redirect("transfer_days_request")
    return render(request, "employee_view/transfer_days_request.html")


def cancel_vacation_days(request):
    return render(request, "employee_view/cancel_vacation_days.html")

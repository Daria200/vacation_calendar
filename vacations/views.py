import datetime
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

from employees.models import Employee

from .models import AvailableDays, PublicHolidays, Request, VacationDay


def verify_days():
    """
    Using start and end date, exclude weekends and public holidays
    Return days to save
    """
    pass


def save_vacation_days_in_db():
    """
    using output of verify_days, save days in the database
    """
    pass


def verify_dates_save_or_reject(
    request,
    startdate,
    enddate,
    employee,
    employee_city,
    vacation_type,
    full_day,
    description,
    request_type,
):
    # Convert the date strings to datetime objects
    start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()

    # Calculate the number of days between the start and end dates
    num_days = (end_date - start_date).days + 1

    # Get Public holidays:
    # Need the city and the year

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
        available_days_instance.allotted_days + available_days_instance.transferred_days
    )

    # Create a list of Vacation instances to save in bulk
    vacation_instances = []

    next_year = current_year + 1
    if request_type == "transfer":
        next_year_record = AvailableDays.objects.get(
            employee=employee,
            year=next_year,
        )
        number_of_transferred_days_next_year = next_year_record.transferred_days

    print("next year")
    print(number_of_transferred_days_next_year)
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
        if request_type == "normal_request":
            if (
                len(vacation_instances) + len(vacation_days_saved_in_db)
                > total_available_days
            ):
                messages.error(
                    request,
                    f"You requested {len(vacation_instances)} days, but you have only {int(total_available_days) - len(vacation_days_saved_in_db)} available days for {current_year}",
                )
            else:
                if request_type == "normal_request":
                    with transaction.atomic():
                        VacationDay.objects.bulk_create(vacation_instances)
                        Request.objects.create(
                            employee=employee,
                            start_date=startdate,
                            end_date=enddate,
                            description=description,
                            request_type=1,
                        )
        elif request_type == "transfer":
            all_transferred = number_of_transferred_days_next_year + len(
                vacation_instances
            )
            if len(vacation_instances) > 10 or all_transferred > 10:
                messages.error(
                    request,
                    f"You can request to transfer up to 10 days.\n"
                    f"You request {len(vacation_instances)}.\n"
                    f"You have {number_of_transferred_days_next_year} transferred days for the nex",
                )
            else:
                with transaction.atomic():
                    # create vacation days and the request
                    VacationDay.objects.bulk_create(vacation_instances)
                    Request.objects.create(
                        employee=employee,
                        start_date=startdate,
                        end_date=enddate,
                        description=description,
                        request_type=2,
                    )
                    # Update available days for the current year
                    available_days_instance = AvailableDays.objects.get(
                        employee=employee, year=current_year
                    )
                    available_days_instance.transferred_days = F(
                        "transferred_days"
                    ) + len(vacation_instances)
                    available_days_instance.save()

                    # Update transferred days for the previous year
                    previous_year = current_year - 1
                    previous_year_available_days = AvailableDays.objects.get(
                        employee=employee, year=previous_year
                    )
                    previous_year_available_days.allotted_days = F(
                        "allotted_days"
                    ) - len(vacation_instances)
                    previous_year_available_days.save()
    return len(vacation_instances)


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
        employee_city = request.user.employee.city

        messages.success(request, f"You requested {number_of_requested_days} days")
        return redirect("vacation_request")

    return render(request, "employee_view/vacation_request.html")


# Check if has available days
# check that the dates are in the first three months of the year
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
        print(description)
        employee_city = request.user.employee.city

        number_of_requested_days = verify_dates_save_or_reject(
            request,
            startdate,
            enddate,
            employee,
            employee_city,
            vacation_type,
            full_day,
            description,
            request_type="transfer",
        )
        # TODO: it is displayed no matter what
        messages.success(request, f"You requested {number_of_requested_days} days")
    return render(request, "employee_view/transfer_days_request.html")


def cancel_vacation_days(request):
    return render(request, "employee_view/cancel_vacation_days.html")

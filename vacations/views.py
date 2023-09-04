import datetime
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from employees.models import Employee

from .models import AvailableDays, PublicHolidays, Request, VacationDay, RemoteDay


def verify_days(
    employee: Employee,
    start_date: date,
    num_days: int,
    start_year: int,
):
    """_summary_

    Args:
        employee Employee: Instance of the Employee class
        start_date date: Date when vacation request starts
        num_days int: Number of days between start and end date icluding weekends and holidays
        start_year int: Year when the vacation starts



    Using start and number of days, exclude weekends and public holidays
    Return only work days

    Returns:
        list of work days
    """

    # Get public holidays for this year
    public_holidays_this_year = PublicHolidays.objects.filter(
        cities=employee.city,
        date__year=year,
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
        current_date = date(year, holiday.date.month, holiday.date.day)
        public_holidays_set.add(current_date)

    work_days = []

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)

        # Exclude weekends (Saturday and Sunday) and public holidays
        if (
            current_date.weekday() not in [5, 6]
            and current_date not in public_holidays_set
        ):
            work_days.append(current_date)
    return work_days


@login_required
def vacation_request(request):
    """_summary_
    Accepts a post request containing start_date, end_date, type and description of
        a vacation request. Excludes weekends and public holidays. Saves days in the database
        and a request with a status of pending.
        Checks if requested days do not exceed allotted+transferred days for the year
    Args:
        request

    Returns:
        redirects to vacation_request
    """

    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        vacation_type = request.POST["vacation_type"]
        duration = float(request.POST["length"])
        description = request.POST.get("description")
        vacation_type = vacation_type

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        start_year = start_date.year
        end_year = end_date.year

        spans_multi_years = start_year != end_year

        vacation_days_saved_in_db = list(
            VacationDay.objects.filter(employee=employee, date__year=start_year)
        )

        num_of_vacation_days_saved_in_db = 0
        for day in vacation_days_saved_in_db:
            num_of_vacation_days_saved_in_db += day.duration

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

        # Excludes weekens and public holidays
        work_days = verify_days(
            employee,
            start_date,
            num_days,
            start_year,
        )
        vacation_instances = []
        for day in work_days:
            vacation_instances.append(
                VacationDay(
                    employee=employee,
                    date=day,
                    duration=duration,
                    approved=False,
                    type=vacation_type,
                    description=description,
                )
            )

        num_of_requested_days = 0
        for day in vacation_instances:
            num_of_requested_days += day.duration

        # Check if the employee does not exceed the available days
        # Get number of available days for the employee
        available_days = AvailableDays.objects.get(employee=employee, year=start_year)

        # Calculate total available days (allotted+transferred)
        total_available_days = (
            available_days.allotted_days + available_days.transferred_days
        )

        if (
            num_of_requested_days
            > int(total_available_days) - num_of_vacation_days_saved_in_db
        ):
            messages.error(
                request,
                f"You requested {len(vacation_instances)} days, but you have only {int(total_available_days) - len(vacation_days_saved_in_db)} available days for {start_year}",
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
            messages.success(request, f"You requested {len(vacation_instances)} days")
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
        duration = "1.0"
        description = request.POST.get("description")

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        start_year = start_date.year
        vacation_days_saved_in_db = VacationDay.objects.filter(
            employee=employee, date__year=start_year
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
        days_to_save_in_db = verify_days(employee, start_date, num_days, start_year)
        available_days_instance = AvailableDays.objects.get(
            employee=employee,
            year=start_year,
        )
        number_of_transferred_days = available_days_instance.transferred_days
        all_transferred = number_of_transferred_days + len(days_to_save_in_db)

        # Check the sum of transferred days for requests that are pending
        pending_requests = Request.objects.filter(
            employee=employee,
            request_type=2,
            request_status=1,
            start_date__year=start_year,
        )
        total_requested_days_pending = 0
        for pending_request in pending_requests:
            num_days = (pending_request.end_date - pending_request.start_date).days + 1
            work_days = verify_days(
                employee,
                pending_request.start_date,
                num_days,
                pending_request.start_date.year,
            )
            total_requested_days_pending += len(work_days)

        total_days_requested_requested_to_transfer = (
            total_requested_days_pending
            + len(days_to_save_in_db)
            + number_of_transferred_days
        )

        if (
            len(days_to_save_in_db) > 10
            or all_transferred > 10
            or total_days_requested_requested_to_transfer > 10
        ):
            messages.error(
                request,
                f"You can request to transfer up to 10 days.\n"
                f"You request {len(days_to_save_in_db)} days.\n"
                f"You have {number_of_transferred_days+total_requested_days_pending} days transferred or requested to transfer  for the next year",
            )
        else:
            vacation_instances = []
            for day in days_to_save_in_db:
                vacation_instances.append(
                    VacationDay(
                        employee=employee,
                        date=day,
                        duration=duration,
                        approved=False,
                        type=vacation_type,
                        description=description,
                    )
                )
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
            messages.success(
                request,
                f"You requested {len(days_to_save_in_db)} days to transfer to {start_year} year",
            )
            return redirect("transfer_days_request")
    return render(request, "employee_view/transfer_days_request.html")


@login_required
def cancel_vacation_days(request):
    # check if the selected days exist in the database
    # create the requst

    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        description = request.POST.get("description")

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        start_year = start_date.year
        vacation_days_saved_in_db = VacationDay.objects.filter(
            employee=employee,
            date__range=(start_date, end_date),
        )
        num_days = (end_date - start_date).days + 1
        days_to_check = verify_days(
            employee=employee,
            start_date=start_date,
            num_days=num_days,
            start_year=start_year,
        )

        all_days_present = True

        for day in days_to_check:
            if not vacation_days_saved_in_db.filter(date=day).exists():
                all_days_present = False
                messages.error(request, f"You have not requested {day}")

        if all_days_present:
            with transaction.atomic():
                Request.objects.create(
                    employee=employee,
                    start_date=startdate,
                    end_date=enddate,
                    description=description,
                    request_type=3,
                )
            messages.success(
                request,
                f"You requested {len(days_to_check)} days to delete",
            )

        return redirect("cancel_vacation_days")
    return render(request, "employee_view/cancel_vacation_days.html")


@login_required
def remote_work_request(request):
    if request.method == "POST":
        user_id = request.user.id
        employee = Employee.objects.get(user_id=user_id)

        # Get form values from the form
        startdate = request.POST["startdate"]
        enddate = request.POST["enddate"]
        description = request.POST.get("description")

        # Get saved days in the database
        start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()
        start_year = start_date.year
        remote_days_saved_in_db = RemoteDay.objects.filter(
            employee=employee, date__year=start_year
        )

        num_of_remote_days_saved_in_db = len(remote_days_saved_in_db)

        remote_days_saved_in_db_list = [
            day.date.strftime("%Y-%m-%d") for day in remote_days_saved_in_db
        ]

        # Check if the record is in the DB
        num_days = (end_date - start_date).days + 1
        for i in range(num_days):
            current_date = start_date + timedelta(days=i)
            if current_date.strftime("%Y-%m-%d") in remote_days_saved_in_db_list:
                messages.error(request, f"You already requested {current_date}")
                return redirect("vacation_request")

        # Excludes weekens and public holidays
        work_days = verify_days(
            employee,
            start_date,
            num_days,
            start_year,
        )
        days_instances = []
        for day in work_days:
            days_instances.append(
                RemoteDay(
                    employee=employee,
                    date=day,
                    approved=False,
                    description=description,
                )
            )

        # Check if the employee does not exceed the available days
        # Get number of available days for the employee
        available_remote_days_instance = AvailableDays.objects.get(
            employee=employee, year=start_year
        )
        num_of_requested_days = len(days_instances)
        if (
            num_of_requested_days
            > available_remote_days_instance.remote_work_days
            - num_of_remote_days_saved_in_db
        ):
            messages.error(
                request,
                f"You requested {num_of_requested_days} days, but you have only {available_remote_days_instance.remote_work_days - num_of_remote_days_saved_in_db} available days for {start_year}",
            )
        else:
            with transaction.atomic():
                RemoteDay.objects.bulk_create(days_instances)
                Request.objects.create(
                    employee=employee,
                    start_date=startdate,
                    end_date=enddate,
                    description=description,
                    request_type=4,
                )
            messages.success(request, f"You requested {num_of_requested_days} days")
        return redirect("remote_work_request")

    return render(request, "employee_view/remote_work_request.html")

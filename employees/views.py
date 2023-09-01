from datetime import date, datetime

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import City, Employee
from vacations.models import AvailableDays


def register(request):
    managers = Employee.objects.filter(is_manager=True)
    if request.method == "POST":
        # Get form values
        first_name = request.POST["first_name"].strip()
        last_name = request.POST["last_name"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"].strip()
        password2 = request.POST["password2"].strip()
        city_name = request.POST["city"]
        manager_id = request.POST["manager"]
        start_date_str = request.POST["start_date"]
        employment_type = request.POST["employment_type"]

        # TODO: validate the manager is in fact a user with is_manager=True
        manager = get_object_or_404(User, id=manager_id)
        city = get_object_or_404(City, name=city_name)

        # check if passwords match
        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            # TODO: does it remove white spaces?
            messages.error(request, "User with this email is already registered")
            return redirect("register")

        current_year = date.today().year
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if start_date.year == current_year:
            end_of_year = date(current_year, 12, 31)
            days_left = (end_of_year - start_date).days + 1
            num_of_days = days_left * 30 / 365
            num_of_days = round(num_of_days * 2) / 2
        else:
            num_of_days = 30

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            employee = Employee.objects.create(
                user=user,
                manager=manager,
                city=city,
                is_manager=False,
                start_date=start_date_str,
                employment_type=employment_type,
            )
            AvailableDays.objects.create(
                employee=employee, allotted_days=num_of_days, year=current_year
            )
        # login after register
        auth.login(request, user)
        # TODO:add message : SUCCESS
        return redirect("calendar")

    cities = City.objects.all()
    context = {"managers": managers, "cities": cities}
    return render(request, "employee_view/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"].strip()
        password = request.POST["password"].strip()
        user = User.objects.get(email=email)
        username = user.username

        user = auth.authenticate(username=username, password=password)

        # TODO: make emails unique and required
        if user is not None:
            auth.login(request, user)
            # ­TODO:add messages
            return redirect("calendar")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")
    return render(request, "employee_view/login.html")


def logout(request):
    if request.method == "POST":
        auth.logout(request)
        messages.success(request, "You are now logged out")
        return redirect("login")

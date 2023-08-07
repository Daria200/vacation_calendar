from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import City, Employee


def register(request):
    managers = Employee.objects.filter(is_manager=True)
    cities = City.objects.all()

    if request.method == "POST":
        # Get form values
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        city_name = request.POST["city"]
        manager_id = request.POST["manager"]
        manager = get_object_or_404(User, id=manager_id)
        city = get_object_or_404(City, name=city_name)

        # check if passwords match
        if password == password2:
            if User.objects.filter(email=email).exists():
                # TODO: does it remove white spaces?
                messages.error(request, "User with this email is already registered")
                return redirect("register")
            else:
                # TODO:what should be the username?
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
                )
                user.save()
                employee.save()
                # login after register
                auth.login(request, user)
                # TODO:add message : SUUCCESS
                return redirect("calendar")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("register")
    else:
        context = {"managers": managers, "cities": cities}
        return render(request, "employee_view/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
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
    return redirect("login")

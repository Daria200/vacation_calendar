from django.shortcuts import redirect, render


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def logout(request):
    return redirect("login")

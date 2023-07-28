from django.shortcuts import redirect, render
from django.contrib import messages


def login(request):
    if request.mothed == "POST":
        print("login")
    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        messages.error(request, 'Testing error message')
        return redirect('register')
    return render(request, "register.html")


def logout(request):
    return redirect("login")

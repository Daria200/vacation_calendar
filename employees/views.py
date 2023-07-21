from django.shortcuts import render


def login(request):
    pass

def register(request):
    return render(request, 'register.html')

def logout(request):
    pass
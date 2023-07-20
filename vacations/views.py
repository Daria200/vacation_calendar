from django.shortcuts import render


# Create your views here.
def add_event(request):
    return render(request, "add_event.html")

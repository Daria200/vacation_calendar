from django.shortcuts import render


# Display employee's own dashboard (short list of the events on the left,
# calender with the days on the right)
# see how many days are used this year
def dashboard(request):
    return render(request, "dashboard.html")


# Managers can view calendars of the employees in the list form
# see how many days are used this year
def employee_calendar(request):
    return render(request, "employee_calendar.html")


# Display employees' own event in a list format
# delete or change days
def events(request):
    return render(request, "events.html")

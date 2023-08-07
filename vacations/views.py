from django.shortcuts import redirect, render


# Create your views here.
def vacation_request(request):
    if request.method == "POST":
        print(request.POST)
        print("hi")
        return redirect("vacation_request")
    return render(request, "employee_view/vacation_request.html")

def transfer_days_request(request):
    return render(request, 'employee_view/transfer_days_request.html')

def cancel_vacation_days(request):
    return render(request, 'employee_view/cancel_vacation_days.html')

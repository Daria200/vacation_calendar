from django.shortcuts import redirect, render


# Create your views here.
def vacation_request(request):
    if request.method == "POST":
        print(request.POST)
        print("hi")
        # Get form values
        # start_date = request.POST["startdate"]
        # enddate = request.POST["end_date"]
        # print(start_date,enddate )
        return redirect(request, "vacation_request")
    return render(request, "vacation_request.html")

def transfer_days_request(request):
    return render(request, 'transfer_days_request.html')

def cancel_vacation_days(request):
    return render(request, 'cancel_vacation_days.html')

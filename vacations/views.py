from django.shortcuts import redirect, render


# Create your views here.
def add_event(request):
    if request.method == "POST":
        print(request.POST)
        print("hi")
        # Get form values
        # start_date = request.POST["startdate"]
        # enddate = request.POST["end_date"]
        # print(start_date,enddate )
        return redirect(request, "add_event")
    return render(request, "add_event.html")

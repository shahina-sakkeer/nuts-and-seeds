from django.shortcuts import render


# Create your views here.


def admin_dashboard(request):
    return render(request,"dashboard.html")


def admin_login(request):
    return render(request,"admin_login.html")
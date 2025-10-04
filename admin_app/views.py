from django.shortcuts import render,redirect
from admin_app.forms import AdminLoginForms
from admin_app.decorators import staff_required
from django.contrib.auth import authenticate,login
from django.contrib import messages

# Create your views here.

@staff_required
def admin_dashboard(request):
    return render(request,"dashboard.html")


def admin_login(request):
    if request.method=="POST":
        form=AdminLoginForms(request.POST)
        if form.is_valid():
            u=form.cleaned_data["username"]
            p=form.cleaned_data["password"]
            user=authenticate(request,username=u,password=p)

            if user is not None and user.is_staff:
                login(request,user)
                return redirect("dashboard_home")
            else:
                messages.error(request,"Invalid Credentials or not and Admin!!")
    else:
        form=AdminLoginForms()

    return render(request,"admin_login.html",{"forms":form})
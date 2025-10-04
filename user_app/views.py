from django.shortcuts import render,redirect
from .forms import UserRegistrationForm,UserLoginForm
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import authenticate,login

# Create your views here.

#USER REGISTRATION VIEW#
def register(request):
    if request.method=="POST":
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active=False
            user.save()

            otp=random.randint(100000,999999)
            cache.set(f"otp:{user.email}", otp, timeout=60)

            send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[user.email])
            messages.success(request,"otp send to the email")
            request.session["pending_email"] = user.email
            return redirect("verify_otp")

    else:
        form = UserRegistrationForm()

    return render(request,"user_signup.html",{"form":form}) 

#OTP VERIFICATION#
def verify_otp(request):
    email = request.session.get("pending_email")
    if request.method=="POST":
        entered_otp=request.POST.get('otp')
        cached_otp = cache.get(f"otp:{email}")

        if cached_otp and str(cached_otp) == entered_otp:
            try:
                user=CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                messages.error(request,"No account found for this email.")
                return redirect("signup")
            
            user.is_active=True
            user.save()
            cache.delete(f"otp:{email}")
            request.session.pop("pending_email", None)
            messages.success(request,"Your account has been verified. Please log in.")
            return redirect("signin")
        else:
            messages.error(request,"Invalid or expired OTP.")
            return redirect("verify_otp")
        
    return render(request,"verify_otp.html",{"email":email})

#RESEND OTP#
def resend_otp(request):
    email = request.session.get("pending_email")
    otp=random.randint(100000,999999)
    cache.set(f"otp:{email}", otp, timeout=60)
    send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[email])
    messages.info(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")
      
#USER LOGIN#
def signin(request):
    if request.method =="POST":
        form=UserLoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get("email")
            password=form.cleaned_data.get("password")
            user=authenticate(request,email=email,password=password)

            if user is not None:
                if user.is_active and not user.is_blocked:
                    login(request,user)
                    messages.success(request, "Login successful!")
                    return redirect("home")
                elif user.is_blocked:
                    messages.error(request,"Your account is blocked")
                else:
                    messages.error(request,"Your account is not activated, Please verify your email.")
            else:
                messages.error(request,"Invalid email or password")
        else:
            messages.error(request, "Invalid form data. Please try again.")
    else:
        form=UserLoginForm()

    return render(request,"user_signin.html",{"form":form})

#FORGOT PASSWORD#
def forgot_password(request):
    if request.method=="POST":
        email=request.POST.get("email")

        try:
            user=CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            messages.error(request,"No account found for this email.")
            return redirect("forgotpswd")
        
        otp=random.randint(100000,999999)
        cache.set(f"reset_otp:{email}",otp,timeout=300)
        request.session["reset_email"]=email
        send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[user.email])
        messages.success(request,"Otp for forgot password has been send to email.")
        return redirect("forgot_password_otp")

    return render(request,"forgot_password.html")

#VERIFY FORGOT OTP#
def verify_forgot_otp(request):
    email=request.session.get("reset_email")
    if not email:
        messages.error(request,"Session expired. Try again.")
        return redirect("forgotpswd")
    if request.method == "POST":
        entered_otp=request.POST.get('otp')
        cached_otp = cache.get(f"reset_otp:{email}")
        if str(entered_otp) == str(cached_otp):
            cache.delete(f"reset_otp:{email}")
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP. Try again.")
    return render(request,"forgot_otp.html")

#RESET PASSWORD#
def reset_password(request):
    email=request.session.get("reset_email")

    #checking reset email is there in the session ie, expired or timeout
    if not email:
        messages.error(request,"Session expired. Try again.")
        return redirect("forgotpswd")
    if request.method=="POST":
        password1=request.POST.get("password1")
        password2=request.POST.get("password2")

        if password1 != password2:
            messages.error(request,"Password do not match")
            return redirect("reset_password")
        else:
            try:
                user=CustomUser.objects.get(email__iexact=email)
            except CustomUser.DoesNotExist:
                messages.error(request,"No user found. Please restart the process.")

            user.set_password(password1)
            user.save()

            del request.session["reset_email"]
            messages.success(request, "Password reset successful! Please login.")
            return redirect("signin")
    return render(request,"password_reset.html")

#HOME PAGE#
def home_page(request):
    return render(request,"home.html")
from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegistrationForm,UserLoginForm
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import authenticate,login,logout
from admin_app.models import Products,Category,ProductVariant
from django.db.models import Q,Min,Max
from django.contrib.auth.decorators import login_required

# Create your views here.

#USER REGISTRATION VIEW#

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    
    if request.method=="POST":
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user_data=form.cleaned_data
            user_data["password"]=form.cleaned_data["password"]
          

            otp=random.randint(100000,999999)
            print(f'otp:{otp}')
            cache.set(f"otp:{user_data['email']}", otp, timeout=60)
            cache.set(f"user_data:{user_data['email']}",user_data,timeout=60)

            send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[user_data['email']])
            messages.success(request,"otp send to the email")
            request.session["pending_email"] = user_data['email']
            return redirect("verify_otp")

    else:
        form = UserRegistrationForm()

    return render(request,"user_signup.html",{"form":form}) 

#OTP VERIFICATION#

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def verify_otp(request):    
    email = request.session.get("pending_email")

    if not email:
        return redirect("signin")
    
    if request.method=="POST":
        entered_otp=request.POST.get('otp')
        cached_otp = cache.get(f"otp:{email}")
        user_data=cache.get(f"user_data:{email}")

        if cached_otp and str(cached_otp) == entered_otp:
            try:

                if not user_data:
                    raise CustomUser.DoesNotExist
                
                user=CustomUser.objects.create(email=user_data['email'],phone_number=user_data['phone_number'],
                firstname=user_data['firstname'],lastname=user_data['lastname'],password=user_data['password'],is_active=True)

                user.set_password(user_data['password'])
                user.save()
             
            except CustomUser.DoesNotExist:
                messages.error(request,"No account found for this email.")
                return redirect("signup")
            
            
            cache.delete(f"otp:{email}")
            cache.delete(f"user_data:{email}")
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

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def signin(request):
    if request.user.is_authenticated:
        return redirect("home")
    
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

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def forgot_password(request):
    if request.session.get("reset_email"):
        return redirect("forgot_password_otp")
    
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
            request.session["otp_verified"] = True
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
            del request.session["otp_verified"]
            messages.success(request, "Password reset successful! Please login.")
            return redirect("signin")
    return render(request,"password_reset.html")

#HOME PAGE#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required
def home_page(request):
    category=Category.objects.all().order_by("-id")
    products=Products.objects.all().order_by("-id")
    return render(request,"home.html",{"products":products,"category":category})


#logout#
def signout(request):
    logout(request)
    cache.clear()
    return redirect("signin")

def landing(request):
    categories=Category.objects.all().order_by("-id")
    products=Products.objects.all().order_by("-id")
    return render(request,"landing.html",{"products":products,"category":categories})


#LIST CATEGORY PRODUCTS
def products_by_category(request,id):
    category=get_object_or_404(Category,id=id)
    products=Products.objects.filter(category=category).prefetch_related("variants").all()
    return render(request,"products_by_catg.html",{"products":products})

#LISTING ALL PRODUCTS
def list_products(request):
    categories=Category.objects.all().order_by("-id")
    products=Products.objects.all().order_by("-id")
    return render(request,"list_by_products.html",{"products":products,"categories":categories})

#FILETRING AND SORTING
def filterProducts(request,id=None):
    search=request.GET.get("search")
    id=request.GET.get("category_id")
    sort=request.GET.get("sort")
    min_price=request.GET.get("minimum")
    max_price=request.GET.get("maximum")
    products=Products.objects.prefetch_related("variants","images").all()

    if id: 
        category=get_object_or_404(Category,id=id)   
        products=Products.objects.filter(category=category).prefetch_related("variants").all()

    if search:
        products=products.filter(name__icontains=search).order_by("-id")
        
    if sort:
        try:
            if sort=="name_asc":
                products=products.order_by("name")
            elif sort=="name_desc":
                products=products.order_by("-name")
            elif sort=="price_asc":
                products=products.annotate(minim_price=Min("variants__price")).order_by("minim_price")
            else:
                products=products.annotate(maxim_price=Max("variants__price")).order_by("-maxim_price")
            
        except ValueError:
            pass
    
    if min_price and max_price:
        try:
            min_price=float(min_price)
            max_price=float(max_price)

            if min_price < max_price:
                products=products.filter(variants__price__gte=min_price,variants__price__lte=max_price).distinct()
        except ValueError:
            pass


    return render(request,"partial_filter.html",{"products":products})


#PRODUCT DETAILS PAGE
def productDetail(request,id=id):
    product=get_object_or_404(Products,id=id)
    variants=product.variants.all()
    first_variant=variants.first()
    return render(request,"product_detail.html",{"prod":product,"variants":variants,"first":first_variant})


def weightFilter(request,id):
    product_variant=get_object_or_404(ProductVariant,id=id)
    return render(request,"partial_detail.html",{"variant":product_variant})

from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .forms import UserRegistrationForm,UserLoginForm,UserAddressForm,UserProfileForm,OrderReturnForm
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.cache import cache_control,never_cache
from django.contrib import messages
from .models import CustomUser,UserAddress,Cart,CartItem,Orders,OrderItem,Wallet,WalletTransaction,OrderReturn,Wishlist,WishlistItem
from django.contrib.auth import authenticate,login,logout
from admin_app.models import Products,Category,ProductVariant,Coupon,CouponUsage
from django.db.models import Q,Min,Max,F,Sum
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.db import transaction
import razorpay,json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
from user_app.helpers import get_offer_price


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

    if not email:
        return JsonResponse({"success": False, "message": "No pending email"}, status=400)
    
    if request.method=="POST":

        otp=random.randint(100000,999999)
        cache.set(f"otp:{email}", otp, timeout=60)
        send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[email])
        messages.info(request, "A new OTP has been sent to your email.")
        return JsonResponse({"success": True, "message": "OTP resent successfully"})
      

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
    # if request.session.get("reset_email"):
    #     return redirect("forgot_password_otp")
    
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
@login_required(login_url='/user/login/')
def home_page(request):
    category=Category.objects.all().order_by("-id")
    products=Products.objects.all().order_by("-id")
    return render(request,"home.html",{"products":products,"category":category})


#logout#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='/user/login/')
def signout(request):
    logout(request)
    cache.clear()
    return redirect("signin")

def landing(request):
    categories=Category.objects.all().order_by("-id")
    products=Products.objects.all().order_by("-id")
    return render(request,"landing.html",{"products":products,"category":categories})


#LIST CATEGORY PRODUCTS
@never_cache
@login_required(login_url='/user/login/')
def products_by_category(request,id):
    category=get_object_or_404(Category,id=id)
    products=Products.objects.filter(category=category).prefetch_related("variants").all()

    return render(request,"products_by_catg.html",{"products":products})

#LISTING ALL PRODUCTS
@never_cache
@login_required(login_url='/user/login/')
def list_products(request):
    categories=Category.objects.all().order_by("-id")
    # products=Products.objects.all().order_by("-id")
    products=Products.objects.prefetch_related("variants","images").all()

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_product_ids = list(
                wishlist.wishlistitem.values_list("product_id", flat=True)
            )

    for product in products:
        for variant in product.variants.all():
            variant.final_price,variant.discount_percent=get_offer_price(variant)
    
    return render(request,"list_by_products.html",{"products":products,"categories":categories,
                                                   "wishlist_product_ids":wishlist_product_ids})


#FILETRING AND SORTING
@never_cache
@login_required(login_url='/user/login/')
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

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_product_ids = list(
                wishlist.wishlistitem.values_list("product_id", flat=True)
            )
    
    for product in products:
        for variant in product.variants.all():
            variant.final_price,variant.discount_percent=get_offer_price(variant)

    return render(request,"partial_filter.html",{"products":products,"wishlist_product_ids":wishlist_product_ids})


#DISPLAYING ALL WISHLIST PRODUCTS
def wishlist_list(request):
    wishlist=Wishlist.objects.filter(user=request.user).first()
    wishlist_items=WishlistItem.objects.filter(wishlist=wishlist).select_related('product','product__product').prefetch_related('product__product__images').order_by('product__product').distinct('product__product')
    return render(request,"wishlist/wishlist.html",{"items":wishlist_items})


# ADDING TO WISHLIST
def add_to_wishlist(request,id):
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    product=get_object_or_404(ProductVariant,id=id)

    existing_item=WishlistItem.objects.filter(wishlist=wishlist,product=product).first()

    if existing_item:
        existing_item.delete()
        messages.success(request,"Removed from wishlist")
        in_wishlist = False
      

    else:
        WishlistItem.objects.create(wishlist=wishlist,product=product)
        messages.success(request,"Added to wishlist")
        in_wishlist = True
        

    return render(request,"partial_wishlist.html",{"product":product,"in_wishlist":in_wishlist})
    

#REMOVE FROM WISHLIST
def remove_from_wishlist(request,id):
    item=get_object_or_404(WishlistItem,id=id)
    if request.method=="POST":
        item.delete()
        return redirect("addWishlist")



#PRODUCT DETAILS PAGE
@never_cache
@login_required(login_url='/user/login/')
def productDetail(request,id=id):
    product=get_object_or_404(Products,id=id)
    variants=list(product.variants.all())

    for variant in variants:
        variant.final_price,variant.discount_percent=get_offer_price(variant)

    # is_available=variants.quantity_stock > 0
        
    first_variant=variants[0] if variants else None

    return render(request,"product_detail.html",{"prod":product,"first":first_variant,"variants":variants})

#PARTAIL PRODUCT VARIANT
@never_cache
@login_required(login_url='/user/login/')
def weightFilter(request,id):
    product_variant=get_object_or_404(ProductVariant,id=id)

    product_variant.final_price,product_variant.discount_percent=get_offer_price(product_variant)

    return render(request,"partial_detail.html",{"variant":product_variant})


#ADD HOME ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def add_address(request):
    if request.method=="POST":
        form=UserAddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect("showAddress")

    else:
        form=UserAddressForm()
    return render(request,"profile/add_address.html",{"form":form})


#SHOW HOME ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def show_address(request):
    user=request.user
    addresses=user.useraddress.all()
    return render(request,"profile/address.html",{"addresses":addresses})


#EDIT ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def edit_address(request,id):
    address=get_object_or_404(UserAddress,id=id,user=request.user)
    
    if request.method=="POST":
        form=UserAddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,"Address updated !!")
            return redirect("showAddress")
    else:
        form=UserAddressForm(instance=address)

    return render(request,"profile/edit_address.html",{"form":form,"address":address})


#DELETE ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def delete_address(request,id):
    address=get_object_or_404(UserAddress,id=id,user=request.user)
    if request.method=="POST":
        address.delete()
        if request.headers.get("HX-Request"): 
            return HttpResponse("")  
        messages.success(request, "Address deleted !!")
        return redirect("showAddress")
    
    return redirect("showAddress")

#SHOW PROFLE
@never_cache
@login_required(login_url='/user/login/')
def show_profile(request):
    user=request.user
    return render(request,"profile/profile.html",{"user":user})

@never_cache
@login_required(login_url='/user/login/')
def user_dashboard(request):
    return render(request,"profile/dashboard.html")


#EDIT PROFILE
@never_cache
@login_required(login_url='/user/login/')
def edit_profile(request):
    user=request.user
    if request.method=="POST":
        form=UserProfileForm(request.POST,instance=user)
        if form.is_valid():
            user_data=form.cleaned_data

            otp=random.randint(100000,999999)
            print(f'otp:{otp}')
            cache.set(f"otp:{user_data['email']}", otp, timeout=60)
            cache.set(f"user_data:{user_data['email']}",user_data,timeout=60)

            send_mail("OTP Verification", f"Your OTP is {otp}. It will expire in 1 minute.", "shahinabinthsakkeer@gmail.com",[user_data['email']])
            messages.success(request,"otp send to the email")
            request.session["pending_email"] = user_data['email']
            return redirect("emailChangeOtp")

    else:
        form=UserProfileForm(instance=user)
        
    return render(request,"profile/edit_profile.html",{"form":form})


#OTP FOR EMAIL CHANGE
@never_cache
@login_required(login_url='/user/login/')
def email_change_otp(request):
    email = request.session.get("pending_email")

    if request.method=="POST":
        entered_otp=request.POST.get('otp')
        cached_otp = cache.get(f"otp:{email}")
        user_data=cache.get(f"user_data:{email}")

        if cached_otp and str(cached_otp) == entered_otp:
            try:

                if not user_data:
                    raise CustomUser.DoesNotExist
                
                user=CustomUser.objects.filter(id=request.user.id).update(email=user_data['email'],phone_number=user_data['phone_number'],
                firstname=user_data['firstname'])
            
             
            except CustomUser.DoesNotExist:
                messages.error(request,"No account found for this email.")
                return redirect("editProfile")
            
            
            cache.delete(f"otp:{email}")
            cache.delete(f"user_data:{email}")
            request.session.pop("pending_email", None)

            messages.success(request,"Your account has been verified. Please log in.")
            return redirect("signin")
        else:
            messages.error(request,"Invalid or expired OTP.")
            return redirect("emailChangeOtp")
        
    return render(request,"profile/email_change_otp.html",{"email":email})


#ADD PRODUCT TO CART
@never_cache
@login_required(login_url='/user/login/')
def add_to_cart(request,id):
    product=get_object_or_404(ProductVariant,id=id)

    offer_price,discount_percent=get_offer_price(product)

    try:
        cart=Cart.objects.get(user=request.user)

    except Cart.DoesNotExist:
        cart=Cart.objects.create(user=request.user)

    # this is a queyset of cartitem model
    # this cartitem is taking only first object from queryset
    cart_item=CartItem.objects.filter(cart=cart,product=product).first()
    if cart_item:
        cart_item.quantity=cart_item.quantity+1
        cart_item.save()

    else:
        cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1)

    return redirect("showCart")


#SHOW CART
@never_cache
@login_required(login_url='/user/login/')
def show_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)

    cart_items=(cart.cart_item.select_related('product__product').prefetch_related('product__product__images'))
    cart_total=0

    for item in cart_items:
        offer_price,discount_percent=get_offer_price(item.product)
        item.final_price=offer_price
        item.discount_percent=discount_percent
        item.row_total=offer_price * item.quantity
        cart_total+=item.row_total
    
    return render(request,"cart/cart.html",{"cart_items":cart_items,"total":cart_total})


#UPDATING QUANTITY IN CART
@never_cache
@login_required(login_url='/user/login/')
def update_quantity(request,id=id):
    item=get_object_or_404(CartItem,id=id,cart__user=request.user)
    action=request.POST.get("action")

    if action=="increase":
        item.quantity=item.quantity+1
        item.product.quantity_stock=item.product.quantity_stock-1
    elif action=="decrease" and item.quantity > 1:
        item.quantity=item.quantity-1
        item.product.quantity_stock=item.product.quantity_stock

    item.save()

    offer_price, discount_percent=get_offer_price(item.product)
    row_total=item.quantity * offer_price

    cart_item=CartItem.objects.filter(cart=item.cart)
    cart_total=0
    for ci in cart_item:
        price,_=get_offer_price(ci.product)
        cart_total+=ci.quantity * price

    return render(request,"cart/partial_quantity.html",{"product":item,"price":row_total,"total":cart_total})


# REMOVE PRODUCT FROM CART
@never_cache
@login_required(login_url='/user/login/')
def remove_from_cart(request,id):
    item=get_object_or_404(CartItem,id=id,cart__user=request.user)
    if request.method=="POST":
        item.delete()
        messages.success(request,"Item deleted !!")
        return redirect("showCart")


#CHECKOUT LIST ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def list_address(request):
    addresses=UserAddress.objects.filter(user=request.user)
    selected_address=addresses.filter(is_primary=True).first()

    if request.method=="POST":
        selected_address_id=request.POST.get("selected_address")
        print("selected address id",selected_address_id)

        if selected_address_id:
            addresses.update(is_primary=False)
            selected_address=addresses.filter(id=selected_address_id).first()
            if selected_address:
                selected_address.is_primary=True
                selected_address.save()

    return render(request,"checkout/address_list.html",{"address":addresses,"default_address": selected_address })


#CHECKOUT PARTIAL ADD NEW ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def add_new_address(request):
    if request.method=="POST":
        form=UserAddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=request.user
            address.save()
            return render(request, "checkout/partial_address_show.html", {"address": address,"user":request.user,"default_address":address})

    else:
        form=UserAddressForm()
    return render(request,"checkout/partial_checkout.html",{"form":form})


#CHECKOUT PAGE
@never_cache
@login_required(login_url='/user/login/')
def checkout(request):
    try:
        cart=Cart.objects.get(user=request.user)

        addresses=UserAddress.objects.filter(user=request.user)

        cart_items=(cart.cart_item.select_related('product__product').prefetch_related('product__product__images'))

        total_price=0 
        for item in cart_items:
            offer_price,discount_percent=get_offer_price(item.product)
            item.final_price=offer_price
            item.discount_percent=discount_percent
            item.row_total=offer_price * item.quantity
            total_price+=item.row_total

        # getting the coupon from session that is set in partial coupon
        coupon_data=request.session.get("coupon_data")

        if coupon_data:
            discount_amount=Decimal(str(coupon_data.get("discount",0)))
            new_price=Decimal(str(coupon_data.get("new_total")))
            coupon_code=coupon_data.get("code")

            # the total price after coupon discount is set in variable payable_amount
            payable_amount=new_price

        else:
            discount_amount=Decimal(0)
            new_price=Decimal(0)
            coupon_code=None

            # if coupon is not applied, take the previous total_price only
            payable_amount=total_price

        if request.method=="POST":
            selected_address_id=request.POST.get("selected_address")
         
            payment_method=request.POST.get("payment_method")

            if not selected_address_id:
                messages.error(request,"Select one address")
                return redirect("checkOut")

            selected_address=UserAddress.objects.get(id=selected_address_id,user=request.user)

            if not payment_method:
                messages.error(request,"Select a payment method")
                return redirect("checkOut")
        

            if payment_method=="cod":
                if total_price > 1000:
                    messages.error(request,"COD is not available for order above 1000.")
                    return redirect("checkOut")
                
            
                with transaction.atomic():
                    for item in cart_items:
                        product=item.product
                        # if product.quantity_stock < item.quantity:
                        #     raise Exception("Insufficient stock")
                        product.quantity_stock-=item.quantity
                        product.save()
                                            
                    order=Orders.objects.create(user=request.user,address=selected_address,item_count=cart_items.count(),
                                   payment_method=payment_method, is_paid=False, total_price=payable_amount,
                                   discount=discount_amount)
                    
                    #creating order items with offer price. unit price is set to offer price, so unit price wont change with changing offer price
                    order_items=[]
                    for item in cart_items:
                        offer_price,discount_percent=get_offer_price(item.product)
                        unit_price=Decimal(offer_price)
                        total_price_per_item=unit_price * item.quantity

                        order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity, 
                                           price=total_price_per_item, unit_price=unit_price))
                    
                    OrderItem.objects.bulk_create(order_items)

                    cart.cart_item.all().delete()
                    
                    if coupon_code:
                        coupon=Coupon.objects.filter(code=coupon_code).first()

                        if coupon:
                            usage,created=CouponUsage.objects.get_or_create(user=request.user,coupon=coupon)
                            usage.used_count+=1
                            usage.save()

                    # create a session of coupon details to pass inside order_placed view
                    request.session["order_data"]={
                        "order_id":order.id,"coupon_code":coupon_code,"discount_amount":str(discount_amount),
                        "grand_total":str(new_price)
                    }

                    # the getted session is deleted 
                    request.session.pop("coupon_data",None)

                    messages.success(request,"Order placed successfully.")
                    return redirect("orderSuccess",id=order.id)

 
            elif payment_method=="razorpay":
                try:
                    request.session.pop("razorpay_order_data", None)
                    request.session.pop("coupon_data", None)

                    client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))

                    razorpay_order = client.order.create({
                        "amount": int(payable_amount * 100),
                        "currency": "INR",
                        "payment_capture": 1
                    })

                    order = Orders.objects.create(
                    user=request.user,
                    address=selected_address,
                    item_count=cart_items.count(),
                    payment_method='razorpay',
                    is_paid=False,
                    total_price=payable_amount,
                    discount=discount_amount,
                    razorpay_order_id=razorpay_order["id"],
                )
                    order_items=[]
                    for item in cart_items:
                        offer_price,discount_percent=get_offer_price(item.product)
                        unit_price=Decimal(offer_price)
                        total_price_per_item=unit_price * item.quantity

                        order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity,
                                           price=total_price_per_item, unit_price=unit_price))
                    
                    OrderItem.objects.bulk_create(order_items)

                    request.session["razorpay_order_data"]={
                        "order_id":razorpay_order["id"],
                        "amount":str(payable_amount),
                        "coupon_code":coupon_data["code"] if coupon_data else None,
                        "discount":coupon_data["discount"] if coupon_data else 0,
                        "new_total":coupon_data["new_total"] if coupon_data else str(payable_amount)
                    }

                    # Send order details to frontend
                
                    return JsonResponse({
                        "key": settings.RAZORPAY['KEY_ID'],
                        "amount": int(payable_amount * 100),
                        "order_id": razorpay_order["id"],
                        "currency": "INR",
                        "local_order_id":order.id
                    })

                
                except Exception as e:
                    print(f"Razorpay order creation failed: {e}")
                    return JsonResponse({"error": "Failed to create Razorpay order."}, status=500)

            elif payment_method=="wallet":
                wallet=Wallet.objects.get(user=request.user)
                if payable_amount <= wallet.balance:

                    with transaction.atomic():
                        for item in cart_items:
                            product=item.product
                            # if product.quantity_stock < item.quantity:
                            #     raise Exception("Insufficient stock")
                            product.quantity_stock-=item.quantity
                            product.save()
                                            
                        order=Orders.objects.create(user=request.user,address=selected_address,item_count=cart_items.count(),
                                   payment_method=payment_method, is_paid=False, total_price=payable_amount,
                                   discount=discount_amount)
                    
                        order_items=[]
                        for item in cart_items:
                            offer_price,discount_percent=get_offer_price(item.product)
                            unit_price=Decimal(offer_price)
                            total_price_per_item=unit_price * item.quantity

                            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity, 
                                           price=total_price_per_item, unit_price=unit_price))

                        cart.cart_item.all().delete()

                        wallet.balance-=payable_amount
                        wallet.save()

                        WalletTransaction.objects.create(wallet=wallet, amount=payable_amount,is_paid=True,
                                                         transaction_type='debit')
                    
                        if coupon_code:
                            coupon=Coupon.objects.filter(code=coupon_code).first()

                            if coupon:
                                usage,created=CouponUsage.objects.get_or_create(user=request.user,coupon=coupon)
                                usage.used_count+=1
                                usage.save()

                    # create a session of coupon details to pass inside order_placed view
                        request.session["order_data"]={
                            "order_id":order.id,"coupon_code":coupon_code,"discount_amount":str(discount_amount),
                            "grand_total":str(new_price)
                        }

                        # the getted session is deleted 
                        request.session.pop("coupon_data",None)

                        messages.success(request,"Order placed successfully.")
                        return redirect("orderSuccess",id=order.id)

                else:
                    messages.error(request,"Insufficient balance in wallet.")
                    return redirect("checkOut")
                
    except UserAddress.DoesNotExist:
        messages.error(request, "Please select an address before placing the order.")
        return redirect("checkOut")

    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect("showCart")

    return render(request,"checkout/checkout.html",{"address":addresses,
                                                "item":cart_items,"totalprice" : total_price})


#CHECKOUT AFTER COUPON IS APPLIED
def partial_coupon(request):
    total_price=Decimal(request.POST.get("total_price",0))
    discount_amount=0
    applied_coupon=None
    error_message=None
    new_total=total_price

    if request.method=="POST":
        coupon_code=request.POST.get("coupon")
   
        if coupon_code:
            coupon=Coupon.objects.filter(code=coupon_code).first()
            if not coupon or not coupon.is_active:
                error_message = "Invalid coupon code."
                
            elif timezone.now() < coupon.start_date or timezone.now() > coupon.end_date:
                error_message="Coupon is not valid currently"
            

            elif total_price < coupon.minimum_purchase_amount:
                error_message="Cart total does not meet the minimum amount."
            
            else:    
                usage,_=CouponUsage.objects.get_or_create(user=request.user,coupon=coupon)

                if usage.used_count < coupon.usage_limit:
                    if coupon.discount_type=="percentage":
                        discount_amount=total_price*coupon.discount_value/100
                    else:
                        discount_amount=coupon.discount_value

                    applied_coupon=coupon
                    new_total=total_price-discount_amount

                    # storing the coupon discount details in a session
                    request.session["coupon_data"]={
                        "code":coupon.code,"discount":str(discount_amount),"new_total":str(total_price-discount_amount)
                    }
                else:
                    error_message="Coupon usage limt reached"

          
        return render(request,"checkout/partial_coupon.html",{"totalprice":total_price,"discount":discount_amount,
                            "applied_coupon":applied_coupon, "new_total":new_total,"error_message":error_message})
    

def partial_coupon_list(request):
    # coupons=Coupon.objects.filter(is_active=True,end_date__gte=timezone.now()).distinct().all()
    coupons=Coupon.objects.all()
    return render(request,"checkout/partial_coupon_list.html",{"coupons":coupons})
    

#VERIFY PAYMENT IN RAZORPAY
@csrf_exempt
@login_required(login_url='/user/login/')
def verify_payment(request):
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            selected_address_id=data.get('selected_address')

            client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }

            client.utility.verify_payment_signature(params_dict)

            #get the order creating in checkout view
            order=Orders.objects.filter(razorpay_order_id=razorpay_order_id,user=request.user).first()

            if not order:
                return JsonResponse({"status": "failure", "message": "Order not found."}, status=404)
            
            if order:
                order.is_paid=True
                order.razorpay_order_id=razorpay_order_id
                order.save()

            cart = Cart.objects.get(user=request.user)
            cart_items = cart.cart_item.select_related('product')

            for item in cart_items:
                        product=item.product
                        # if product.stock_quantity < item.quantity:
                        #     raise Exception("Insufficient stock")
                        product.quantity_stock-=item.quantity
                        product.save()

            order_items=OrderItem.objects.filter(order=order)
            order_items.update(payment_status="paid")

            cart.cart_item.all().delete()
            
            #get the session that was created in checkout view if the payment == razorpay
            razorpay_order_data=request.session.get("razorpay_order_data",None)

            if razorpay_order_data:
                # if coupon is applied
                payable_amount=razorpay_order_data.get("amount",0)
                coupon_code=razorpay_order_data.get("coupon_code")
                new_total=razorpay_order_data.get("new_total",0)
                discount=razorpay_order_data.get("discount",0)

            else:
                # if coupon is not applied 
                total_price=0
                for item in cart_items:
                    offer_price,discount_percent=get_offer_price(item.product)
                    item.final_price=offer_price
                    item.discount_percent=discount_percent
                    item.row_total=offer_price * item.quantity
                    total_price+=item.row_total

                payable_amount=total_price
                coupon_code=None
                discount=Decimal(0)
                new_total=payable_amount        

                if coupon_code:
                        coupon=Coupon.objects.filter(code=coupon_code).first()
                        if coupon:
                            usage,created=CouponUsage.objects.get_or_create(user=request.user,coupon=coupon)
                            usage.used_count+=1
                            usage.save()

                # the getted session is deleted 
                request.session.pop("coupon_data",None)
                request.session.pop("razorpay_order_data",None)

            return JsonResponse({
                "status": "success",
                "order_id": order.id,
                "redirect_url": f"/user/order-success/{order.id}/"
            })

        except razorpay.errors.SignatureVerificationError:
            local_order_id=data.get("local_order_id")
            print("DEBUG: Local order ID from frontend:", data.get("local_order_id"))
            order=Orders.objects.filter(id=local_order_id).first()
            
            if order:
                order.is_paid=False
                order.save()

                OrderItem.objects.filter(order=order).update(payment_status="failed")

                return JsonResponse({"status": "failure", "order_id": order.id,
                                 "redirect_url": f"/user/order-failure/{order.id}/"})
            else:
                return JsonResponse({"status": "failed", "message": "Payment verification failed."})

        except Exception as e:
            local_order_id=data.get("local_order_id")
            order=Orders.objects.filter(id=local_order_id).first()
            if order:
                order.is_paid=False
                order.save()

                OrderItem.objects.filter(order=order).update(payment_status="failed")

                return JsonResponse({"status": "failure", "order_id": order.id,
                                 "redirect_url": f"/user/order-failure/{order.id}/"})
            
            else:
                return JsonResponse({"status": "failed", "message": "Unexpected error occurred."})
        

#ORDER PAYEMENT FAILURE        
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='/user/login/')
def order_failure(request,id):

    order=get_object_or_404(Orders,id=id)
    print(order.id)
    order_item=OrderItem.objects.filter(order=order,payment_status="failed")
    print(order_item)

    return render(request,"order/order_failure.html",{"items":order_item,"order":order})



#ORDER SUCCESSFULLY PLACES
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='/user/login/')
def order_placed(request,id=id):
    order=get_object_or_404(Orders,id=id,user=request.user)
    latest_order=Orders.objects.filter(user=request.user).order_by("-created_at").first()
    order_item=OrderItem.objects.filter(order=latest_order).all()

    original_total = sum(item.price for item in order_item)

    return render(request,"order/order_placed.html",{"items":order_item,"order":latest_order,"og_total":original_total})



#LIST OF ALL ORDERS
@never_cache
@login_required(login_url='/user/login/')
def orders_list(request):
    orders=Orders.objects.filter(user=request.user).prefetch_related('orderitem').order_by("-id")

    for order in orders:
        order.is_failed_payment=order.orderitem.filter(payment_status='failed').exists()
    return render(request,"order/orders_lists.html",{"orders":orders})


#ORDER DETAILED PAGE
@never_cache
@login_required(login_url='/user/login/')
def order_detail(request,id=id):
    order=get_object_or_404(Orders,id=id,user=request.user)
    ordered_item_details=order.orderitem.all()

    original_total = sum(item.price for item in ordered_item_details)

    # order_data=request.session.get("order_data",{})
    # coupon_code=order_data.get("coupon_code")
    # discount_amount=order_data.get("discount_amount",0)
    # grand_total=order_data.get("grand_total",order.total_price)

    if request.method=="POST":
        item_id = request.POST.get("item_id")

        if item_id:
            ordered_item = order.orderitem.get(id=item_id)

            if ordered_item.payment_status=="pending":
                ordered_item.status="cancelled"
                ordered_item.save()
                messages.success(request,"Your order has been cancelled!!")

            elif ordered_item.payment_status=="paid":
                ordered_item.status="cancelled"
                ordered_item.save()
                wallet,created=Wallet.objects.get_or_create(user=request.user)
                wallet.balance+=ordered_item.price
                wallet_txn=WalletTransaction.objects.create(wallet=wallet,amount=ordered_item.price,is_paid=False,
                                transaction_type='credit')
                wallet.save()
                wallet_txn.save()
                messages.success(request,f"Your order has been cancelled.Rs.{ordered_item.price} added to wallet")

        else:
            messages.warning(request,"Order cannot be cancelled")

        return redirect("orderDetail",id=order.id)

    return render(request,"order/order_detail.html",{"orders":ordered_item_details,"order":order,"og_total":original_total})


def return_order_item(request,id=id):
    item=get_object_or_404(OrderItem,id=id,status="delivered")

    if request.method=="POST":
        form=OrderReturnForm(request.POST,request.FILES)
        if form.is_valid():
            return_form=form.save(commit=False)
            return_form.user=request.user
            return_form.item=item
            return_form.status="pending"
            return_form.save()

            item.approval_status="pending"
            item.save()

            messages.success(request,"Your return request has been successfully submitted")
            return redirect("order-list")

    else:
        form=OrderReturnForm()

    return render(request,"order/return_order.html",{"form":form})


#ADD MONEY TO WALLET
def add_money_wallet(request):
    wallet,created=Wallet.objects.get_or_create(user=request.user)

    if request.method=="POST":
        money=Decimal(request.POST.get("amount"))

        if money <= 0:
            messages.error(request,"Invalid amount")
            return redirect("walletList")
        
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))

            razorpay_order = client.order.create({"amount": int(money * 100),
                        "currency": "INR",
                        "payment_capture": 1
                    })

            wallet_txn=WalletTransaction.objects.create(wallet=wallet,amount=money,is_paid=False,
                                transaction_type='credit', razorpay_order_id=razorpay_order["id"])
                    
            # Send order details to frontend 
            return JsonResponse({
                "key": settings.RAZORPAY['KEY_ID'],
                "amount": int(money * 100),
                "order_id": razorpay_order["id"],
                "currency": "INR",
                "wallet_txn_id":wallet_txn.id
                })
         
        except Exception as e:
            print(f"Razorpay order creation failed: {e}")
            return JsonResponse({"error": "Failed to create wallet."}, status=500)

    # normal html page render on initial load
    transaction=wallet.transaction.all().order_by("-created_at")
    context={
        "balance":wallet.balance,
        "transaction" : transaction}    
    
    # if request is htmx, return the wallet page written in htmx
    if request.headers.get("HX-Request"):
        context={
            "balance" : wallet.balance,
            "wallet_txn" : wallet.transaction.all().order_by("-created_at")
        }
        return render(request, "profile/add_money_wallet.html",context)
        
    return render(request,"profile/add_money_wallet.html",context)


#VERIFY WALLET PAYMENT  
@csrf_exempt
@login_required(login_url='/user/login/')
def wallet_verify_payment(request):
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')

            client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }

            client.utility.verify_payment_signature(params_dict)

            #get the order created in the checkout view
            wallet_txn=WalletTransaction.objects.get(razorpay_order_id=razorpay_order_id)

            if not wallet_txn:
                return JsonResponse({"status": "failure", "message": "Order not found."}, status=404)
            
            if wallet_txn:
                wallet_txn.is_paid=True
                wallet_txn.razorpay_order_id=razorpay_order_id
                wallet_txn.transaction_type='credit'
                wallet_txn.save()

            wallet=wallet_txn.wallet
            wallet.balance+=wallet_txn.amount
            wallet.save()

            return JsonResponse({
                "status": "success", "balance":str(wallet.balance), "amount":str(wallet_txn.amount), 
                                                            "transaction_type": wallet_txn.transaction_type})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "failed", "message": "Payment verification failed."})

        except Exception as e:
            return JsonResponse({"status": "failed", "message": "Unexpected error occurred."})
        



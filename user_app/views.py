from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegistrationForm,UserLoginForm,UserAddressForm,UserProfileForm
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.cache import cache_control,never_cache
from django.contrib import messages
from .models import CustomUser,UserAddress,Cart,CartItem,Orders,OrderItem,Wishlist
from django.contrib.auth import authenticate,login,logout
from admin_app.models import Products,Category,ProductVariant
from django.db.models import Q,Min,Max,F,Sum
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.db import transaction
import razorpay,json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import time


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
    products=Products.objects.all().order_by("-id")
    wishlist_items=[]
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return render(request,"list_by_products.html",{"products":products,"categories":categories,"wishlist_items":wishlist_items})

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

    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request,"partial_filter.html",{"products":products,"wishlist_items":wishlist_items})


def toggle_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(ProductVariant, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            wishlist_item.delete()
            return JsonResponse({'success': True, 'added': False, 'message': 'Removed from wishlist'})
        else:
            return JsonResponse({'success': True, 'added': True, 'message': 'Added to wishlist'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# def add_to_wishlist(request):
#     if request.method=="POST":
#         user=request.user
#         product_id=request.POST.get("product_id")

#         try:
#             product_variant=ProductVariant.objects.get(id=product_id)
#         except ProductVariant.DoesNotExist:
#             messages.error(request,"Product not found")
#             return redirect("all_products")
        
#         wishlist_exist=Wishlist.objects.filter(user=user,product=product_variant).exists()
#         if wishlist_exist:
#             messages.warning(request, "Already in your wishlist.")
#         else:
#             Wishlist.objects.create(user=user,product=product_variant)
#             messages.success(request,"Added to wishlist")
#         return redirect("all_products")
        


#PRODUCT DETAILS PAGE
@never_cache
@login_required(login_url='/user/login/')
def productDetail(request,id=id):
    product=get_object_or_404(Products,id=id)
    variants=product.variants.all()
    first_variant=variants.first()
    return render(request,"product_detail.html",{"prod":product,"variants":variants,"first":first_variant})

#PARTAIL PRODUCT VARIANT
@never_cache
@login_required(login_url='/user/login/')
def weightFilter(request,id):
    product_variant=get_object_or_404(ProductVariant,id=id)
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

    if not product.is_deleted:

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

    cart_items=(cart.cart_item.select_related('product__product')
        .prefetch_related('product__product__images')
        .annotate(row_total=F('quantity') * F('product__price')))
    
    cart_total=cart_items.aggregate(total=Sum('row_total'))['total'] or 0
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

    row_total=item.quantity * item.product.price

    cart_item=CartItem.objects.filter(cart=item.cart).annotate(row_total=F('quantity') * F('product__price'))

    cart_total=cart_item.aggregate(total=Sum('row_total'))['total'] or 0

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


#CHECKOUT PAGE
@never_cache
@login_required(login_url='/user/login/')
def checkout(request):
    try:
        cart=Cart.objects.get(user=request.user)

        addresses=UserAddress.objects.filter(user=request.user)
        select_address=addresses.filter(is_primary=True).first()

        cart_items=(cart.cart_item.select_related('product__product')
            .prefetch_related('product__product__images')
            .annotate(row_total=F('quantity') * F('product__price')))
    
        total_price=cart_items.aggregate(total=Sum('row_total'))['total'] or 0

        if request.method=="POST":
            selected_address_id=request.POST.get("selected_address")
         
            payment_method=request.POST.get("payment_method")
            print(payment_method)

            if selected_address_id:
                select_address=UserAddress.objects.filter(id=selected_address_id,user=request.user).first()

            if not select_address:
                messages.error(request,"Select one address")
                return redirect("checkOut")

            if not payment_method:
                messages.error(request,"Select a payment method")
                return redirect("checkOut")
            
            if payment_method=="cod":
                if total_price < 1000:
                    messages.error(request,"COD is only available for orders above 1000")
                    return redirect("checkOut")
                
                with transaction.atomic():
                    order=Orders.objects.create(user=request.user,address=select_address,item_count=cart_items.count(),
                                   payment_method=payment_method, is_paid=False, total_price=total_price)
                    
                    order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.row_total)
                       for item in cart_items]
                    
                    OrderItem.objects.bulk_create(order_items)
 
            elif payment_method=="razorpay":
                client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))
                try:
                    razorpay_amount = int(float(total_price * 100))
                   
                    razorpay_order = client.order.create({
                        "amount": razorpay_amount,
                        "currency": "INR",
                        "receipt": f"order_rcptid_{request.user.id}_{int(time.time())}",
                        "payment_capture": 1
                    })
                   
                    order=Orders.objects.create(user=request.user,address=select_address,item_count=cart_items.count(),
                                   payment_method=payment_method,razorpay_order_id = razorpay_order["id"], 
                                   is_paid=False, total_price=total_price)
                    
                    order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.row_total)
                       for item in cart_items]
                    
                    OrderItem.objects.bulk_create(order_items)

                    return JsonResponse({"status": "razorpay_created", "razorpay_key": settings.RAZORPAY['KEY_ID'],
                        "razorpay_order_id": razorpay_order["id"],"amount": razorpay_amount,"order_id": order.id})

                except Exception as e:
                    messages.error(request, f"Error during checkout: {e}")
                    return redirect("showCart")
                
            
            cart_items.delete()

            messages.success(request,"Order placed successfully")
            return redirect("orderSuccess",id=order.id)
        
    except UserAddress.DoesNotExist:
        messages.error(request, "Please select an address before placing the order.")
        return redirect("checkOut")

    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect("showCart")

    except Exception as e:
        
        messages.error(request, "Something went wrong while placing your order.")
        print(f"Unexpected error: {e}")
        return redirect("showCart")
    
    return render(request,"order/checkout.html",{"address":addresses,"default_address":select_address,
                                                "item":cart_items,"totalprice" : total_price})


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client = razorpay.Client(auth=(settings.RAZORPAY['KEY_ID'], settings.RAZORPAY['KEY_SECRET']))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            order = Orders.objects.get(razorpay_order_id=data['razorpay_order_id'])
            order.is_paid = True
            order.save()

            return JsonResponse({"status": "success"})

        except razorpay.errors.SignatureVerificationError:
            messages.error(request,"Payment verification failed. Please try again.")
            return redirect("checkOut")



#LIST ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def list_address(request):
    addresses=UserAddress.objects.filter(user=request.user)
    selected_address=addresses.filter(is_primary=True).first()

    if request.method=="POST":
        selected_address_id=request.POST.get("selected_address")
        print("selected address id",selected_address_id)

        if selected_address_id:
            selected_address=addresses.filter(id=selected_address_id).first()

    return render(request,"order/address_list.html",{"address":addresses,"default_address": selected_address })

#PARTIAL ADD NEW ADDRESS
@never_cache
@login_required(login_url='/user/login/')
def add_new_address(request):
    if request.method=="POST":
        form=UserAddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=request.user
            address.save()
            return render(request, "order/partial_address_show.html", {"address": address,"user":request.user,"default_address":address})

    else:
        form=UserAddressForm()
    return render(request,"order/partial_checkout.html",{"form":form})


#ORDER PLACES
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='/user/login/')
def order_placed(request,id=id):
    order=get_object_or_404(Orders,id=id,user=request.user)
    latest_order=Orders.objects.filter(user=request.user).order_by("-created_at").first()
    order_item=OrderItem.objects.filter(order=latest_order).all()
    return render(request,"order/order_placed.html",{"items":order_item,"order":latest_order})


#LIST OF ALL ORDERS
@never_cache
@login_required(login_url='/user/login/')
def orders_list(request):
    orders=Orders.objects.filter(user=request.user).order_by("-id")
    return render(request,"order/orders_lists.html",{"orders":orders})


#ORDER DETAILED PAGE
@never_cache
@login_required(login_url='/user/login/')
def order_detail(request,id=id):
    order=get_object_or_404(Orders,id=id,user=request.user)
    ordered_item_details=order.orderitem.all()

    if request.method=="POST":
        item_id = request.POST.get("item_id")

        if item_id:
            ordered_item = order.orderitem.get(id=item_id)
            if ordered_item.status=="pending":
                ordered_item.status="cancelled"
                ordered_item.save()
                messages.success(request,"Your order has been cancelled!!")
        else:
            messages.warning(request,"Order cannot be cancelled")

        return redirect("orderDetail",id=order.id)

    return render(request,"order/order_detail.html",{"orders":ordered_item_details,"order":order})













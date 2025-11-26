from django.shortcuts import render,redirect,get_object_or_404
from admin_app.forms import AdminLoginForm,CategoryForm,ProductForm,ProductImageForm,ProductVariantFormSet,ProductVariantInlineFormSet,CouponForm,CategoryOfferForm,ProductOfferForm
from admin_app.decorators import staff_required
from django.contrib.auth import authenticate,login,logout
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.contrib import messages
from admin_app.models import Category,Products,ProductImage,ProductVariant,Coupon,CategoryOffer,ProductOffer
from django.db import transaction,IntegrityError
from django.db.models import Q,Sum
from django.core.paginator import Paginator
from user_app.models import CustomUser,Orders,OrderItem,OrderReturn,Wallet,WalletTransaction
import base64
from cloudinary.uploader import upload
from datetime import date,timedelta,datetime
from admin_app.helper import get_sales_data,get_ordered_products,get_ordered_categories
from decimal import Decimal


# Create your views here.

#DASHOBOARD OF ADMIN#
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def admin_dashboard(request):
    filter_type=request.GET.get("filter","today")
    start_date=request.GET.get("start")
    end_date=request.GET.get("end")

    #filter option
    today=date.today()
    start_of_week=today - timedelta(days=today.weekday())
    start_of_month=today.replace(day=1)
    start_of_year=today-timedelta(days=365)

    #overall total
    order_count=Orders.objects.count()
    total_sales=Orders.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_discount=Orders.objects.aggregate(total=Sum('discount'))['total'] or 0
    net_sales=total_sales-total_discount

    orders=Orders.objects.all().order_by("-created_at")[:5]

    if filter_type=="today":
        filtered_data=get_sales_data(today,today)
        products_show = get_ordered_products(today, today)
        categories_show=get_ordered_categories(today,today)

    elif filter_type=="weekly":
        filtered_data=get_sales_data(start_of_week,today)
        products_show = get_ordered_products(start_of_week, today)
        categories_show=get_ordered_categories(start_of_week,today)
        
    elif filter_type=="monthly":
        filtered_data=get_sales_data(start_of_month,today)
        products_show = get_ordered_products(start_of_month, today)
        categories_show=get_ordered_categories(start_of_month,today)

    elif filter_type=="yearly":
        filtered_data=get_sales_data(start_of_year,today)
        products_show = get_ordered_products(start_of_year, today)
        categories_show=get_ordered_categories(start_of_year,today)

    elif filter_type=="custom":
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect("dashboard_home")
        else:
            messages.error(request, "Please select both start and end dates.")
            return redirect("dashboard_home")
        
        filtered_data=get_sales_data(start_date,end_date)
        products_show = get_ordered_products(start_date, end_date)
        categories_show=get_ordered_categories(start_date,end_date)
        

    return render(request,"dashboard.html",{
        "order_count":order_count,
        "total_sales":total_sales,
        "total_discount":total_discount,
        "net_sales":net_sales,
        "filter_type":filter_type,
        "filtered_sales": filtered_data["sales"],
        "filtered_discount": filtered_data["discount"],
        "filtered_net_sales": filtered_data["net"],
        "filtered_count": filtered_data["count"],
        "product_show":products_show,
        "category_show":categories_show,
        "orders":orders
    })



#CUSTOMER MANAGEMENT    
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def customer(request):
    user=CustomUser.objects.filter(is_staff=False,is_superuser=False).order_by("-id")

    paginator=Paginator(user,6)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)
    return render(request,"customers.html",{"users":page_obj})


#BLOCK USER MANAGEMENT
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def blockUser(request,id):
    user=get_object_or_404(CustomUser,id=id)
    if request.method=="POST":
        user.is_blocked=not user.is_blocked
        user.save()
    
    return render(request,"status_column.html",{"user":user})


#ADMIN LOGIN#
def admin_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    
    if request.method=="POST":
        form=AdminLoginForm(request.POST)
        if form.is_valid():
            u=form.cleaned_data["username"]
            p=form.cleaned_data["password"]
            user=authenticate(request,username=u,password=p)

            if user is not None and user.is_staff:
                login(request,user)
                messages.success(request,"Admin login successfully")
                return redirect("dashboard_home")
            else:
                messages.error(request,"Invalid Credentials or not and Admin!!")
    else:
        form=AdminLoginForm()

    return render(request,"admin_login.html",{"form":form})


#ADMIN LOGOUT
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def signout(request):
    logout(request)
    cache.clear()
    return redirect("admin_signin")


#LIST CATEGORY#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def list_category(request):
    categories=Category.objects.all().order_by("-id")

    paginator=Paginator(categories,5)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)

    return render(request,"list_category.html",{"page_obj":page_obj})


#ADD CATEGORY#
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def add_category(request):
    if request.method=="POST":
        form=CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            
            try:
                form.save()
                messages.success(request,"category is successfully added")
            except IntegrityError:
                messages.error(request, "Category already exists")
            return redirect("listCategory")
    else:
        form=CategoryForm()
    return render(request,"add_category.html",{"form":form})


#EDIT CATEGORY#
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def edit_category(request,id):
    category=get_object_or_404(Category,id=id)

    if request.method=="POST":
        form=CategoryForm(request.POST,request.FILES,instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,"Category updated!!")
            return redirect("listCategory")
    else:
        form=CategoryForm(instance=category)

    return render(request,"edit_category.html",{"form":form,"category":category})


#DELETE CATEGORY#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def delete_category(request,id):
    category=get_object_or_404(Category.all_category,id=id)
    category.is_deleted=not category.is_deleted
    category.save()
    return render(request,"restdel_button.html",{"category":category})


#LIST PRODUCTS#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def products(request):
    products=Products.objects.prefetch_related("variants","images").all().order_by("-id")

    paginator=Paginator(products,5)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)
    return render(request,"products.html",{"page_obj":page_obj})


#ADD PRODUCTS#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def add_products(request):
    if request.method=="POST":
        form=ProductForm(request.POST)
        variant_formset=ProductVariantFormSet(request.POST)

        if form.is_valid() and variant_formset.is_valid():
            try:
                product = form.save()
                print("product",product)
            
                for variant_form in variant_formset:
                    if variant_form.cleaned_data:
                        variant = variant_form.save(commit=False)
                        variant.product = product
                        variant.save()

                 
                for i in range(1, 5):
                    cropped_data = request.POST.get(f"cropped_image_{i}")
                    print(f"Image {i} data:", cropped_data[:50] if cropped_data else "No data")
                    if cropped_data:
                        format, imgstr = cropped_data.split(';base64,')
                        ext = format.split('/')[-1]
        
                        img_bytes = base64.b64decode(imgstr)

                 
                        result = upload(img_bytes, folder="products")
                        ProductImage.objects.create(product=product, image=result['secure_url'])
                        print(f"Image {i} uploaded successfully")

                messages.success(request, "Product successfully added")
                print(messages)
                return redirect("listProduct")

            except Exception as e:
                messages.error(request,"Failed to add product")
        
    else:
        form=ProductForm()
        variant_formset=ProductVariantFormSet()

    return render(request,"add_product.html",{"form":form,"variant":variant_formset})


#EDIT PRODUCTS#
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def edit_product(request,id):
    product=get_object_or_404(Products,id=id)
    images=product.images.all()

    if request.method=="POST":
        form=ProductForm(request.POST,request.FILES,instance=product)
        variant_formset=ProductVariantInlineFormSet(request.POST,request.FILES,instance=product)

        if form.is_valid() and variant_formset.is_valid():
          
            try:
                product=form.save()
                    
                for variant_form in variant_formset:
                    if variant_form.cleaned_data:

                        variant=variant_form.save(commit=False)
                        variant.product=product  
                        variant.save()
                    
             
                remove_ids=request.POST.getlist("remove_images")
                if remove_ids:
                    ProductImage.objects.filter(id__in=remove_ids).delete()

                remove_variant_id=request.POST.getlist("remove_variant")
                print(remove_variant_id)
                if remove_variant_id:
                    ProductVariant.objects.filter(id__in=remove_variant_id).delete()

                
                for i in range(1, 5):
                    cropped_data = request.POST.get(f"cropped_image_{i}")
                    if cropped_data and cropped_data.startswith('data:image'):
                        format, imgstr = cropped_data.split(';base64,')
                        ext = format.split('/')[-1]
                        img_bytes = base64.b64decode(imgstr)
                        
                        result = upload(img_bytes, folder="products")
                        ProductImage.objects.create(product=product, image=result['secure_url'])
                        print(f"Image {i} uploaded successfully")

                messages.success(request,"Product updated!!!")
                return redirect("listProduct")
                
            except Exception as e:
                messages.error(request,"Failed to update!. Try again.")
                return redirect("editProduct",id=product.id)

        
    else:
        form=ProductForm(instance=product)
        variant_formset=ProductVariantInlineFormSet(instance=product)

    return render(request,"edit_product.html",{"form":form,"variant":variant_formset,"product":product,"images":images})


#DELETE PRODUCT
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def soft_delete_product(request,id):
    product=get_object_or_404(Products.all_products,id=id)
    product.is_deleted= not product.is_deleted
    product.save()
    return render(request,"delrest_button.html",{"product":product})



#SEARCH PRODUCT
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def search(request):
    search=request.GET.get("search")
    if search:
        products=Products.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search)).order_by("-id")
    else:
        products=Products.objects.prefetch_related("variants", "images").all().order_by("-id")

    return render(request,"partial_product.html",{"products":products})


#SEARCH CATEGORY
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def searchCategory(request):
    search=request.GET.get("search")
    if search:
        categories=Category.objects.filter(name__icontains=search).order_by("-id")
    else:
        categories=Category.objects.all().order_by("-id")

    return render(request,"partial_category.html",{"category":categories})


#ORDERS LIST
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def order_list(request):
    orders=Orders.objects.all().order_by("-id")

    paginator=Paginator(orders,8)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)
    return render(request,"orders/orders.html",{"orders":page_obj})


#ORDER DETAILED PAGE
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def order_detail_page(request,id):
    order=get_object_or_404(Orders,id=id)
    ordered_item_details=order.orderitem.all()
    user=order.user
    address=order.address

    if request.method=="POST":
        item_id=request.POST.get("item_id")
        new_status=request.POST.get("status")

        if item_id and new_status:
            item=get_object_or_404(order.orderitem,id=item_id)
            item.status=new_status
            item.save()
            messages.success(request,f"Order status changed to {new_status}")
            return redirect("orderDetailView",order.id)

    return render(request,"orders/order_detail.html",{"items":ordered_item_details,"order":order})


#ORDER RETURN REQUEST ACTION
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def order_return_request(request,id):
    return_item=get_object_or_404(OrderReturn,id=id,approval_status="pending")
    item=return_item.item
    user=return_item.user
    product=item.product
    
    action=request.POST.get("decision")
    if action=="approve":
        return_item.approval_status="refunded"
        item.status="returned"

        price=Decimal(str(item.price))
        total_before_discount=Decimal(str(item.order.total_price_before_discount))
        discount=Decimal(str(item.order.discount))

        item_discount_share=(price/total_before_discount)*discount

        refund_amount=price-item_discount_share

        wallet,created=Wallet.objects.get_or_create(user=user)
        wallet.balance=Decimal(str(wallet.balance))
        wallet.balance+=refund_amount
        wallet_txn=WalletTransaction.objects.create(wallet=wallet,amount=refund_amount,is_paid=False,
                                transaction_type='credit',source='order_return',order=item.order)
        wallet.save()
        wallet_txn.save()
        item.save()
        return_item.save()

        product.quantity_stock+=item.quantity
        product.save()
        messages.success(request,f"Return request for {item.product.product.name} is approved")
        return redirect("orderDetailView",id=return_item.item.order.id)
        

    elif action=="reject":
        return_item.approval_status="rejected"
        item.status="rejected"
        item.save()
        return_item.save()
        
        messages.info(request,f"Return request for {item.product.product.name} is rejected")
        return redirect("orderDetailView",id=return_item.item.order.id)


#ADD COUPON
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def add_coupon(request):
    if request.method=="POST":
        form=CouponForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,"New Coupon added")
            except IntegrityError:
                messages.error(request, "Coupon already exists")
            return redirect("couponList")
    else:
        form=CouponForm()
    
    return render(request,"coupon/add_coupon.html",{"form":form})


#ADD COUPON
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def list_coupon(request):
    coupon=Coupon.objects.all().order_by("-id")
    return render(request,"coupon/list_coupon.html",{"coupons":coupon})


#DELETE COUPON
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def delete_coupon(request,id):
    coupon=get_object_or_404(Coupon,id=id)
    coupon.delete()
    return redirect("couponList")


#LIST ALL OFFERS
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def all_offers(request):
    category=CategoryOffer.objects.all().order_by("-id")
    products=ProductOffer.objects.all().order_by("-id")

    return render(request,"offer/offers.html",{"category":category,"products":products})


#ADD CATEGORY OFFER
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def add_category_offer(request):
    if request.method=="POST":
        form=CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Offer added")
            return redirect("allOffers")
    else:
        form=CategoryOfferForm()
    return render(request,"offer/category_add_offer.html",{"form":form})


#ADD PRODUCT OFFER
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def add_product_offer(request):
    if request.method=="POST":
        form=ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Offer added")
            return redirect("allOffers")
    else:
        form=ProductOfferForm()
    return render(request,"offer/product_add_offer.html",{"form":form})


#DELETE CATEGORY OFFER
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def delete_category_offer(request,id):
    category_offer=get_object_or_404(CategoryOffer,id=id)
    category_offer.delete()
    return redirect("allOffers")


#DELETE PRODUCT OFFER
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@staff_required
def delete_product_offer(request,id):
    product_offer=get_object_or_404(ProductOffer,id=id)
    product_offer.delete()
    return redirect("allOffers")


def list_wallet(request):
    wallet_txn=WalletTransaction.objects.all().order_by("-created_at")

    paginator=Paginator(wallet_txn,8)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)

    return render(request,"wallet/list_wallet.html",{"wallet_txn":page_obj})


def wallet_details(request,id):
    wallet_txn=get_object_or_404(WalletTransaction,id=id)
    return render(request,"wallet/detail_wallet.html",{"txn":wallet_txn})






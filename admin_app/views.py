from django.shortcuts import render,redirect,get_object_or_404
from admin_app.forms import AdminLoginForm,CategoryForm,ProductForm,ProductImageForm,ProductVariantFormSet,ProductVariantInlineFormSet
from admin_app.decorators import staff_required
from django.contrib.auth import authenticate,login,logout
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.contrib import messages
from admin_app.models import Category,Products,ProductImage,ProductVariant
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator
from user_app.models import CustomUser
import base64
from cloudinary.uploader import upload


# Create your views here.

#DASHOBOARD OF ADMIN#
@staff_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def admin_dashboard(request):
    return render(request,"dashboard.html")


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
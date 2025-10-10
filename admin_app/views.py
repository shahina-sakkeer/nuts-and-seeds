from django.shortcuts import render,redirect,get_object_or_404
from admin_app.forms import AdminLoginForm,CategoryForm,ProductForm,ProductImageForm,ProductVariantFormSet,ProductVariantInlineFormSet
from admin_app.decorators import staff_required
from django.contrib.auth import authenticate,login
from django.contrib import messages
from admin_app.models import Category,Products,ProductImage
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator


# Create your views here.

#DASHOBOARD OF ADMIN#
@staff_required
def admin_dashboard(request):
    return render(request,"dashboard.html")


#ADMIN LOGIN#
def admin_login(request):
    if request.method=="POST":
        form=AdminLoginForm(request.POST)
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
        form=AdminLoginForm()

    return render(request,"admin_login.html",{"form":form})


#LIST CATEGORY#
def list_category(request):
    categories=Category.objects.all().order_by("-id")
    return render(request,"list_category.html",{"category":categories})


#ADD CATEGORY#
def add_category(request):
    if request.method=="POST":
        form=CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            new_name=form.cleaned_data["name"]
            if Category.all_category.filter(name__iexact=new_name).exists():
                messages.error(request,"category already there")
                return redirect("addCategory")
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
def edit_category(request,id):
    category=get_object_or_404(Category,id=id)

    if request.method=="POST":
        form=CategoryForm(request.POST,request.FILES,instance=category)
        if form.is_valid():
            new_name=form.cleaned_data["name"]
            if Category.objects.filter(name__iexact=new_name).exclude(id=category.id).exists():
                messages.error(request,"name already exists")
                return redirect("editCategory",id=id)

            form.save()
            return redirect("listCategory")
    else:
        form=CategoryForm(instance=category)

    return render(request,"edit_category.html",{"form":form,"category":category})


#DELETE CATEGORY#
def delete_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_deleted=True
    category.save()
    messages.success(request,"deletion succesfull")
    return redirect("listCategory")


#RESTORE CATEGORY
def restore_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_deleted=False
    category.save()
    messages.success(request,"category restored")
    return redirect("listCategory")



#LIST PRODUCTS#
def products(request):
    products=Products.objects.prefetch_related("variants","images").all().order_by("-id")
    return render(request,"products.html",{"products":products})


#ADD PRODUCTS#
def add_products(request):
    if request.method=="POST":
        form=ProductForm(request.POST)
        variant_formset=ProductVariantFormSet(request.POST)
        image_form=ProductImageForm()
        images=request.FILES.getlist("images")

        if form.is_valid() and variant_formset.is_valid():
            try:
                with transaction.atomic():
                    product=form.save()

                    for variant_form in variant_formset:
                        if variant_form.cleaned_data:

                            variant=variant_form.save(commit=False)
                            variant.product=product  
                            variant.save()

                    for img in images:
                            ProductImage.objects.create(product=product,image=img)
                    
                    messages.success(request,"product is successfully added")
                    return redirect("listProduct")
                
            except Exception as e:
                messages.error(request,f"error is {e}")
    else:
        form=ProductForm()
        variant_formset=ProductVariantFormSet()
        image_form=ProductImageForm()

    return render(request,"add_product.html",{"form":form,"variant":variant_formset,"image":image_form})


#EDIT PRODUCTS#

def edit_product(request,id):
    product=get_object_or_404(Products,id=id)
    existing_images=product.images.all()

    if request.method=="POST":
        form=ProductForm(request.POST,instance=product)
        variant_formset=ProductVariantInlineFormSet(request.POST,instance=product)
        image_form=ProductImageForm()
        images=request.FILES.getlist("images")
        delete_img_id=request.POST.getlist("delete_images")

        if form.is_valid() and variant_formset.is_valid():
            print("loaded")
            
            try:
                with transaction.atomic():
                    product=form.save()
                    
                    for variant_form in variant_formset:
                        if variant_form.cleaned_data:

                            variant=variant_form.save(commit=False)
                            variant.product=product  
                            variant.save()

                    if delete_img_id:
                        
                        ProductImage.objects.filter(id__in=delete_img_id,product=product).delete()
                        print("delete")

                        for img in images:
                            ProductImage.objects.create(product=product,image=img)
                            

                        # messages.success(request,"product updates successfully")
                        return redirect("listProduct")
                
            except Exception as e:
                print("failed loading",e)
                return redirect("editProduct")
    else:
        form=ProductForm(instance=product)
        variant_formset=ProductVariantInlineFormSet(instance=product)
        image_form=ProductImageForm()

    return render(request,"edit_product.html",{"form":form,"variant":variant_formset,"exist_img":existing_images,"image":image_form})


#DELETE PRODUCT
def soft_delete_product(request,id):
    product=get_object_or_404(Products,id=id)
    product.is_deleted=True
    product.save()
    messages.success(request,"deletion succesfull")
    return redirect("listProduct")


#RESTORE PRODUCT
def restore_product(request,id):
    product=get_object_or_404(Products,id=id)
    product.is_deleted=False
    product.save()
    messages.success(request,"product restored")
    return redirect("listProduct")


#SEARCH PRODUCT
def search(request):
    q=request.GET.get("q")
    if q:
        products=Products.objects.filter(Q(name__icontains=q) | Q(category__name__icontains=q)).order_by("-id")
    else:
        products=Products.objects.prefetch_related("variants", "images").all().order_by("-id")

    return render(request,"partial_product.html",{"products":products})


#SEARCH CATEGORY
def searchCategory(request):
    q=request.GET.get("q")
    if q:
        categories=Category.objects.filter(name__icontains=q).order_by("-id")
    else:
        categories=Category.objects.all().order_by("-id")

    return render(request,"partial_category.html",{"category":categories})
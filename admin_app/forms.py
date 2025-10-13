from django import forms
from admin_app.models import Category,Products,ProductVariant,ProductImage
from django.forms import formset_factory,ValidationError,inlineformset_factory
import re
    
class AdminLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={
        "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
        "placeholder": "Username"
    }))
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
        "placeholder": "Password"
    }))


class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=["id","name","description","image"]

    widgets={
        "name": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter name",
                "autocomplete": "off"
            }),
        "description": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter descr",
                'autocomplete': 'off'
            }),

    }

    def clean_name(self):
        name=self.cleaned_data.get("name")
        if name and not re.match(r'^[a-zA-Z\s]+$', name):
            raise ValidationError("Category name must contain only letters and spaces (no numbers or special characters)")
        
        if Category.all_category.filter(name__iexact=name).exclude(id=self.instance.id).exists():
                raise ValidationError("A category with this name already exists")
        return name

class ProductForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=["id","category","name","description","status"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter product name",'autocomplete': 'off'
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter product description",
                "rows": 3
            }),
            "category": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
        }

    def clean_name(self):
        name=self.cleaned_data.get("name")
        if name and not re.match(r'^[a-zA-Z\s]+$', name):
            raise ValidationError("Category name must contain only letters and spaces (no numbers or special characters)")
        
        
        return name
    

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model=ProductVariant
        fields=["id","weight","unit","quantity_stock","price"]
        widgets={
            "weight": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Weight"
            }),
            "unit": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "quantity_stock": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Quantity in stock"
            }),
            "price": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Price"
            })
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model=ProductImage
        fields=["image"]


ProductVariantFormSet=formset_factory(ProductVariantForm,extra=3)

ProductVariantInlineFormSet=inlineformset_factory(Products,ProductVariant,form=ProductVariantForm,extra=0)
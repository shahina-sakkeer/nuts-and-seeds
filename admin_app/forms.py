from django import forms
from admin_app.models import Category,Products,ProductVariant,ProductImage,Coupon,CategoryOffer,ProductOffer,Banner
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
            "status": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
        }

    def clean_name(self):
        name=self.cleaned_data.get("name")
        if name and not re.match(r'^[a-zA-Z\s]+$', name):
            raise ValidationError("Product name must contain only letters and spaces (no numbers or special characters)")
        
        
        return name
    

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model=ProductVariant
        fields=["id","weight","unit","quantity_stock","price","status"]
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
            }),
            "status": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
        }


    def clean(self):
        cleaned_data=super().clean()
        price=cleaned_data.get("price")
        weight=cleaned_data.get("weight")
        quantity_stock=cleaned_data.get("quantity_stock")

        if price is not None and price<0:
            self.add_error("price","Price cannot be negative number")

        if weight is not None and weight<0:
            self.add_error("weight","Weight cannot be negative number")

        if quantity_stock is not None and quantity_stock<0:
            self.add_error("quantity_stock","Stock value cannot be negative number")

        return cleaned_data

class ProductImageForm(forms.ModelForm):
    class Meta:
        model=ProductImage
        fields=["id","image"]


ProductVariantFormSet=formset_factory(ProductVariantForm,extra=3,can_delete=True)

ProductVariantInlineFormSet=inlineformset_factory(Products,ProductVariant,form=ProductVariantForm,extra=2,
                                                  max_num=3,can_delete=True)


class CouponForm(forms.ModelForm):
    class Meta:
        model=Coupon
        fields=["code","discount_type","minimum_purchase_amount","usage_limit","maximum_discount_limit",
                "start_date","end_date","is_active","description","discount_value"]
        
        widgets={
            "code": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Coupon code"
            }),
            "discount_type": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "discount_value": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Discount value"
            }),
            "minimum_purchase_amount": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Minimum amount"
            }),
            "usage_limit": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Limit"
            }),
            "start_date": forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent "
                        "calendar-icon",
            "placeholder": "Start Date",
            }),
            "end_date": forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent "
                         "calendar-icon",
            "placeholder": "End Date",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter product description",
                "rows": 3
            }),
            "maximum_discount_limit":forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter maximum discount"
            }),
        }


    def clean_minimum_purchase_amount(self):
        minimum_purchase_amount=self.cleaned_data.get("minimum_purchase_amount")
        if minimum_purchase_amount and minimum_purchase_amount <= 0:
            raise ValidationError("Invalid purchase amount.")
        
        return minimum_purchase_amount
    

    def clean_maximum_discount_limit(self):
        maximum_discount_limit=self.cleaned_data.get("maximum_discount_limit")
        if maximum_discount_limit and maximum_discount_limit <= 0:
            raise ValidationError("Invalid limit.")
        
        return maximum_discount_limit


    def clean_usage_limit(self):
        usage_limit=self.cleaned_data.get("usage_limit")
        if usage_limit and usage_limit<=0:
            raise ValidationError("Value must be greater than 0")
        
        return usage_limit
    

    def clean(self):
        cleaned_data=super().clean()
        discount_type=cleaned_data.get("discount_type")
        discount_value=cleaned_data.get("discount_value")
        minimum_purchase_amount=cleaned_data.get("minimum_purchase_amount")
        start_date=self.cleaned_data.get("start_date")
        end_date=self.cleaned_data.get("end_date")

        if discount_type=="percentage":
            if discount_value is not None and discount_value <= 0 or discount_value > 70:
                self.add_error("discount_value", "Percentage discount must be between 1% and 70%.")


        if discount_type=="flat":
            if discount_value is not None and discount_value <= 0:
                self.add_error("discount_value","Discount amount cannot be less than 0.")

            if discount_value and minimum_purchase_amount:
                if discount_value > minimum_purchase_amount:
                    self.add_error("discount_value","Flat discount cannot be greater than minimum purchase amount.")  


        if start_date and end_date is not None:
            if end_date < start_date:
                self.add_error('end_date','End date cannot be less than start date.')
            elif end_date==start_date:
                self.add_error('end_date','Start date and end date cannot be same.')      

        return cleaned_data



class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model=CategoryOffer
        fields=["id","category","offer_percentage","start_date","end_date","is_active"]

        widgets={
            "category": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "offer_percentage": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Offer precentage"
            }),
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Start Date",
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "End Date",
            }),
        }


    def clean_offer_percentage(self):
        offer_percentage=self.cleaned_data.get("offer_percentage")
        if offer_percentage and offer_percentage<=0 or offer_percentage>=100:
            raise ValidationError("Offer value should be from 0% to 100%")
        
        return offer_percentage
    
    def clean(self):
        cleaned_data=super().clean()
        start_date=self.cleaned_data.get("start_date")
        end_date=self.cleaned_data.get("end_date")

        if start_date and end_date is not None:
            if end_date < start_date:
                self.add_error('end_date','End date cannot be less than start date.')
            elif end_date==start_date:
                self.add_error('end_date','Start date and end date cannot be same.')


        return cleaned_data


class ProductOfferForm(forms.ModelForm):
    class Meta:
        model=ProductOffer
        fields=["id","product","offer_percentage","start_date","end_date","is_active"]


        widgets={
            "product": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "offer_percentage": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Offer precentage"
            }),
            "start_date": forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Start Date",
            }),
            "end_date": forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "End Date",
            }),
        }


    def clean_offer_percentage(self):
        offer_percentage=self.cleaned_data.get("offer_percentage")
        if offer_percentage and offer_percentage<=0 or offer_percentage>=100:
            raise ValidationError("Offer value should be from 0% to 100%.")
        
        return offer_percentage
    
    def clean(self):
        cleaned_data=super().clean()
        start_date=self.cleaned_data.get("start_date")
        end_date=self.cleaned_data.get("end_date")

        if start_date and end_date is not None:
            if end_date < start_date:
                self.add_error('end_date','End date cannot be less than start date.')
            elif end_date==start_date:
                self.add_error('end_date','Start date and end date cannot be same.')

        return cleaned_data
    


class BannerForm(forms.ModelForm):
    class Meta:
        model=Banner
        fields=["name","image"]
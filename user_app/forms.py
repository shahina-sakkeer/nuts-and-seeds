from django import forms
from .models import CustomUser,UserAddress
from django.forms import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Enter your password",
            'autocomplete': 'off'
        }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Enter your password",
            'autocomplete': 'off'
        }))

    class Meta:
        model=CustomUser
        fields=["email","firstname","lastname","phone_number"]

        widgets = {
            "firstname": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your first name",
                'autocomplete': 'off'
            }),
            "lastname": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your last name",
                'autocomplete': 'off'
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your email",
                'autocomplete': 'off'
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your phone name",
                'autocomplete': 'off'
            })
        }

    def clean(self):
        cleaned_data=super().clean()
        password=cleaned_data.get("password")
        confirm_password=cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("password","Passwords doesnot match")
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if password and not re.match(pattern, password):
            self.add_error("password",
                "Password must be at least 8 characters long, ""contain at least one uppercase letter, one lowercase letter, and one digit."
            )
        return cleaned_data

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
        "placeholder": "Enter your email",
        'autocomplete': 'off'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
        "placeholder": "Enter your password",
        'autocomplete': 'off'
    }))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=["email","firstname","phone_number"]


class UserAddressForm(forms.ModelForm):
    class Meta:
        model=UserAddress
        fields=["house_name","street","landmark","city","pincode","state"]

    def clean_house_name(self):
        house_name=self.cleaned_data.get("house_name")
        
        if UserAddress.objects.filter(house_name__iexact=house_name).exclude(id=self.instance.id).exists():
                raise ValidationError("This house name already exists")
        return house_name
    
    def clean_pincode(self):
        pincode=self.cleaned_data.get("pincode")
        
        if len(str(pincode)) < 6:
            raise forms.ValidationError("Pincode must be at least 8 digits long.")
        
        if int(pincode) < 0:
            raise forms.ValidationError("Pincode cannot be negative")
        
        return pincode
    

    def clean(self):
        cleaned_data=super().clean()
        city=cleaned_data.get("city")
        state=cleaned_data.get("state")

        if city and not city.isalpha():
            self.add_error("city","City can only contains alphabets")

        if state and not state.isalpha():
            self.add_error("state","State can only contains alphabets")

        return cleaned_data





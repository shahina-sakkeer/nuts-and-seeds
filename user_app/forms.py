from django import forms
from .models import CustomUser
import re

class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Enter your password"
        }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Enter your password"
        }))

    class Meta:
        model=CustomUser
        fields=["email","firstname","lastname","phone_number"]

        widgets = {
            "firstname": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your first name"
            }),
            "lastname": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your last name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your email"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter your phone name"
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
        "placeholder": "Enter your email"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
        "placeholder": "Enter your password"
    }))
from django import forms
from .models import CustomUser,UserAddress,OrderReturn
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
    referral_code=forms.CharField(required=False,
            widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Referral code (Optional)",
            'autocomplete': 'off',
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
        fields=["firstname","phone_number","referralID"]

        widgets={
            "firstname": forms.TextInput(attrs={
                "class": "w-full bg-gray-100 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "firstname",
                'autocomplete': 'off'
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "w-full bg-gray-100 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "phone number",
                'autocomplete': 'off'
            }),
        }


class UserAddressForm(forms.ModelForm):
    class Meta:
        model=UserAddress
        fields=["house_name","street","landmark","city","pincode","state"]

        widgets = {
            "house_name": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "Address",
                'autocomplete': 'off'
            }),
            "street": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "Street",
                'autocomplete': 'off'
            }),
            "landmark": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "Landmark",
                'autocomplete': 'off'
            }),
            "city": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "City",
                'autocomplete': 'off'
            }),
            "pincode": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "Pincode",
                'autocomplete': 'off'
            }),
            "state": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "State",
                'autocomplete': 'off'
            })
        }

    # def clean_house_name(self):
    #     house_name=self.cleaned_data.get("house_name")
        
    #     if UserAddress.objects.filter(house_name__iexact=house_name).exclude(id=self.instance.id).exists():
    #             raise ValidationError("This house name already exists")
    #     return house_name
    
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



class OrderReturnForm(forms.ModelForm):
    class Meta:
        model=OrderReturn
        fields=['return_choice','image','return_reason']

        widgets={
        "return_choice": forms.RadioSelect(),
        "return_reason": forms.TextInput(attrs={
                "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
                "placeholder": "Enter reason",
                'autocomplete': 'off'
            }),
        "image": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-gray-700 border border-gray-300 rounded-md cursor-pointer "
                         "bg-gray-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
            }),
    }


    def clean_return_reason(self):
        return_reason=self.cleaned_data.get('return_reason')

        if len(return_reason)<10:
            raise ValidationError("Reason should contains atleast 10 characters long")
        
        if return_reason and not re.match(r'^[a-zA-Z\s]+$', return_reason):
            raise ValidationError("Reason should contain only alphabets")
        
        return return_reason

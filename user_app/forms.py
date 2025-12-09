from django import forms
from .models import CustomUser,UserAddress,OrderReturn,Review
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
    referral_code=forms.CharField(required=False, widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
            "placeholder": "Referral code (Optional)",
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
                "placeholder": "Enter your phone number",
                'autocomplete': 'off'
            }),
        }

    def clean(self):
        cleaned_data=super().clean()
        password=cleaned_data.get("password")
        confirm_password=cleaned_data.get("confirm_password")
        firstname=cleaned_data.get("firstname")
        lastname=cleaned_data.get("lastname")

        if password and confirm_password and password != confirm_password:
            self.add_error("password","Passwords doesnot match")
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if password and not re.match(pattern, password):
            self.add_error("password",
                "Password must be at least 8 characters long, ""contain at least one uppercase letter, one lowercase letter, and one digit."
            )

        if firstname and not firstname.isalpha():
            self.add_error("firstname","Name should contain only alphabets")

        if lastname and not lastname.isalpha():
            self.add_error("lastname","Name should contain only alphabets")

        return cleaned_data
    

    def clean_referral_code(self):
        code=self.cleaned_data.get("referral_code")
        email=self.cleaned_data.get("email")
        phone_number=self.cleaned_data.get("phone_number")

        referrer=CustomUser.objects.filter(referralID=code).first()

        if code:
            if not referrer:
                raise forms.ValidationError("Invalid referral code")

            if referrer.email==email or referrer.phone_number==phone_number:
                raise forms.ValidationError("You cannot use your own referral code")
            
        return code
    

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
        fields=["firstname","lastname","phone_number"]

        widgets={
            "firstname": forms.TextInput(attrs={
                "class": "w-full bg-gray-100 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "first name",
                'autocomplete': 'off'
            }),
            "lastname": forms.TextInput(attrs={
                "class": "w-full bg-gray-100 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "last name",
                'autocomplete': 'off'
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "w-full bg-gray-100 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:outline-none",
                "placeholder": "phone number",
                'autocomplete': 'off',
            }),
        }


    def clean(self):
        cleaned_data=super().clean()
        firstname=cleaned_data.get("firstname")
        lastname=cleaned_data.get("lastname")

        if firstname and not firstname.isalpha():
            self.add_error("firstname","Name should contain only alphabets")

        if lastname and not lastname.isalpha():
            self.add_error("lastname","Name should contain only alphabets")

        return cleaned_data


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

  
    
    def clean_pincode(self):
        pincode=self.cleaned_data.get("pincode")
        
        if len(str(pincode)) != 6:
            raise forms.ValidationError("Pincode must be 6 digits long.")
        
        if int(pincode) < 0:
            raise forms.ValidationError("Pincode cannot be negative")
        
        return pincode
    

    def clean(self):
        cleaned_data=super().clean()
        house_name=cleaned_data.get("house_name")
        street=cleaned_data.get("street")
        landmark=cleaned_data.get("landmark")
        city=cleaned_data.get("city")
        state=cleaned_data.get("state")

        if house_name and not re.match(r'^[A-Za-z0-9 ]+$', house_name):
            self.add_error("house_name","Please enter a proper house name")

        if street and not re.match(r'^[A-Za-z0-9 ]+$', street):
            self.add_error("street","Please enter a proper street name")

        if landmark and not re.match(r'^[A-Za-z0-9 ]+$', landmark):
            self.add_error("landmark","Please enter a proper landmark")

        if city and not city.isalpha():
            self.add_error("city","City can only contains alphabets")

        if state and not state.isalpha():
            self.add_error("state","State can only contains alphabets")

        if city and len(city)<4:
            self.add_error("city","City should contains atleast 4 characters")

        if state and len(state)<4:
            self.add_error("state","State should contains atleast 4 characters")


        return cleaned_data



class OrderReturnForm(forms.ModelForm):
    image=forms.ImageField(
        error_messages={
            "invalid_image": "Only PNG, JPG, JPEG, WEBP files are allowed.",
        }
    )

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


    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        if hasattr(image, "content_type"):
            allowed = ["image/png", "image/jpeg", "image/webp"]

            if image.content_type not in allowed:
                raise ValidationError("Only PNG, JPG, JPEG, WEBP allowed.")    

        return image
    


class ReviewForm(forms.ModelForm):
    image=forms.ImageField(
        error_messages={
            "invalid_image": "Only PNG, JPG, JPEG, WEBP files are allowed.",
        }
    )

    class Meta:
        model=Review
        fields=["comment","rating","image"]

        widgets={
            "comment":forms.TextInput(attrs={
                "class":"w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none resize-none",
                "placeholder":"Comment you experiance"
            }),
        }


    def clean_comment(self):
        comment=self.cleaned_data.get("comment")

        if len(comment)<3:
            raise forms.ValidationError("Comments should contain atleast 3 letters")
        
        return comment
    
    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        if hasattr(image, "content_type"):
            allowed = ["image/png", "image/jpeg", "image/webp"]

            if image.content_type not in allowed:
                raise ValidationError("Only PNG, JPG, JPEG, WEBP allowed.")    

        return image



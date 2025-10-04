from django import forms

class AdminLoginForms(forms.Form):
    username=forms.CharField(max_length=150)
    password=forms.CharField(widget=forms.PasswordInput)
    
# class AdminLoginForm(forms.forms):
#     username=forms.CharField(widget=forms.TextInput(attrs={
#         "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
#         "placeholder": "Username"
#     }))
#     password=forms.CharField(widget=forms.PasswordInput(attrs={
#         "class": "w-full px-3 py-3 border border-gray-300 rounded-md placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent",
#         "placeholder": "Password"
#     }))


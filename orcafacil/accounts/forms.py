from django import forms
from .models import UserProfile,CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email','password','accept_email']

class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email','password']
from django import forms
from .models import UserProfile,CustomUser,Company

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email','password','accept_email']

class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email','password']
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'accept_email']

    def clean_password(self):
        # ignora o campo password, se vier por engano
        return self.instance.password
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model= UserProfile
        fields= "__all__"
        exclude = ['user']

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"
        exclude = ['user']
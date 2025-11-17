from django import forms
from .models import UserProfile,CustomUser,Company

class CustomUserForm(forms.ModelForm):
    
    confirm_password = forms.Field(
        label = "Confirme sua senha",
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder' : "Confirme sua senha",

            }
        )
    )
    def __init__(self, *args,**kargs):
        super().__init__(*args,**kargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
                label_text = field.label if field.label else field_name.replace('_', ' ').title()
                field.widget.attrs['placeholder'] = label_text

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email','password', 'confirm_password','accept_email', 'accept_terms']
        labels = {
            "password": "Senha" ,
            "accept_email":'Aceito receber emails',
            'accept_terms':"Aceito os termos"
        }   
        help_texts = {
                'email': 'Utilize um e-mail válido. Será usado para login e notificações.'
            }
        error_messages = {
            'email': {
                'unique': 'Este e-mail já está cadastrado',
                'invalid': 'Insira um e-mail válido'
            }
        }
       
    def clean_accept_terms(self):
        accept = self.cleaned_data.get('accept_terms')
        if not accept:
            raise forms.ValidationError("Você precisa aceitar os termos para continuar.")
        return accept

    def clean(self):

        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "As senham precisam ser iguais.")
        return cleaned_data

class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email','password']
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'accept_email']
        errors = {
            ""
        }

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
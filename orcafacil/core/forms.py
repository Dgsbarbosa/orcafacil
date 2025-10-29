from django.forms import ModelForm
from .models import Client, Budget

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'lastname','phone', 'email','street','number','complement',"neighborhood",'city','state', 'zipcode','obs']
from django.forms import ModelForm
from .models import Client, Budget

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['__all__']
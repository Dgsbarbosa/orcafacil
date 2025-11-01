from django.forms import ModelForm
from .models import Client, Budget,Services
from django.forms import inlineformset_factory

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'lastname','phone', 'email','street','number','complement',"neighborhood",'city','state', 'zipcode','obs']

class BudgetForm(ModelForm):

    class Meta:
        model = Budget
        fields = ['client', 'title',   'status']

    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # pega o usuário passado pela view
        super().__init__(*args, **kwargs)
        if user:
            # filtra apenas os clientes do usuário logado
            self.fields['client'].queryset = Client.objects.filter(user=user)

class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = ['service', 'description', 'quantity', 'unit_price']             

ServiceFormSet = inlineformset_factory(
    Budget, Services,
    form=ServicesForm,
    extra=1,
    can_delete=False
)
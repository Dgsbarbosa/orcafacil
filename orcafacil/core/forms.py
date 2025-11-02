from django import forms
from django.forms import ModelForm
from .models import Client, Budget,Services
from django.forms import inlineformset_factory

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['status','name', 'lastname','phone', 'email','street','number','complement',"neighborhood",'city','state', 'zipcode','obs']

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
    # Campo somente visual — não será salvo
    subtotal = forms.DecimalField(
        label="Subtotal",
        required=False,
        disabled=True,
        decimal_places=4,
        max_digits=15
    )

    class Meta:
        model = Services
        # ⚠️ NÃO inclui subtotal aqui!
        fields = ['service', 'description', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define o subtotal inicial (somente visual)
        if self.instance and self.instance.pk:
            subtotal = (
                self.instance.subtotal_budget
                if getattr(self.instance, "subtotal_budget", None)
                else self.instance.subtotal()
            )
            self.fields['subtotal'].initial = subtotal
        else:
            self.fields['subtotal'].initial = 0


ServiceFormSet = inlineformset_factory(
    Budget,
    Services,
    form=ServicesForm,
    extra=1,
    can_delete=True
)

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django import forms
from django.utils import timezone


class AddressMixin(models.Model):
    street = models.CharField(max_length=255,verbose_name="Endereço")

    number = models.CharField(max_length=20, verbose_name="Número", null=True, blank=True)
    complement = models.CharField(max_length=150, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    state = models.CharField(max_length=100, verbose_name="Estado", blank=True, null=True)
    zipcode = models.CharField(max_length=15, verbose_name="CEP", blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"



    def __str__(self):
        
        fomated_address = f" {self.street}, {self.number}, {self.complement}, {self.neighborhood}, {self.city}, {self.state}, {self.country}, {self.zipcode}"
        return fomated_address

    
class Client(AddressMixin):

    STATUS_CLIENT_CHOICES = [
        ("inativo","Inativo"),
        ("ativo","Ativo")
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,verbose_name="Nome")
    lastname = models.CharField(max_length=100,verbose_name='Sobrenome')
    phone = models.CharField(max_length=20, blank=True,verbose_name='Telefone')
    email = models.EmailField(blank=True,verbose_name='Email', unique=True)
    obs = models.TextField(blank=True,verbose_name='Observação')

    status = models.CharField(choices=STATUS_CLIENT_CHOICES, default="ativo")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email

        # Verifica se existe outro cliente com o mesmo e-mail
        qs = Client.objects.filter(email=email)

        # Se estiver editando, exclui o próprio ID da busca
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Este e-mail já está cadastrado para outro cliente.")

        return email
    def __str__(self):
        return f'{self.name} {self.lastname} '

class Budget(models.Model):
    STATUS_CHOICES = [
        ('pendente',"Pendente"),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('cancelado','Cancelado')

    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente")
    
    code = models.CharField(max_length=20,unique=True)
    
    title = models.CharField(max_length=100, verbose_name="Título")
   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', 
    verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            year = timezone.now().year
            count = Budget.objects.filter(user=self.user, created_at__year=year).count() + 1
            self.code = f"{count:03d}-{year}"

            # Evita duplicidade rara em gravação simultânea
            while Budget.objects.filter(code=self.code).exists():
                count += 1
                self.code = f"{count:03d}-{year}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title}"
    

class Services(models.Model):
    
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='services')

    service = models.CharField(max_length=100, verbose_name='Serviço')

    description = models.TextField(blank=True, null=True, verbose_name='Descrição')

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")

    def subtotal(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f'{self.service} - ({self.budget.code}-{self.budget.title})'
from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.conf import settings
from django import forms
from django.utils import timezone
from accounts.models import UserProfile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from common.models import AddressMixin, SoftDeleteModel

    
class Client(AddressMixin,SoftDeleteModel):

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

class Budget(SoftDeleteModel):
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
    
    
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Total")
    obs = models.TextField(verbose_name='Observaçoes')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            year = timezone.now().year

            # Pega o último código criado no mesmo ano
            last_budget = (
                Budget.objects.filter(user=self.user, created_at__year=year)
                .aggregate(last_code=Max("code"))
            )["last_code"]

            if last_budget:
                # Extrai a parte numérica (antes do "-")
                last_number = int(last_budget.split("-")[0])
                next_number = last_number + 1
            else:
                # Primeiro orçamento do ano
                next_number = 1

            # Monta o código no formato 001-2025
            self.code = f"{next_number:03d}-{year}/{self.user.id}"

        super().save(*args, **kwargs)

    def __str__(self):

        self.code = self.code.split("/")
        return f"{self.code[0]} - {self.title}"
    
    def update_total(self):
        total_services = sum(s.subtotal() for s in self.services.all())
        total_materials = sum(m.subtotal() for m in self.materials.all())
        self.total_value = total_services + total_materials
        self.save(update_fields=['total_value'])

    

class Services(models.Model):
    
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='services')

    service = models.CharField(max_length=100, verbose_name='Serviço')

    description = models.TextField(blank=True, null=True, verbose_name='Descrição')

    quantity = models.DecimalField(max_digits=10, decimal_places=2,default=1, verbose_name='Quantidade', null=True, blank=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário",null=True, blank=True)

    subtotal_services = models.DecimalField(max_digits=15, decimal_places=2,verbose_name='Subtotal')

    def subtotal(self):

        try:
            return self.quantity * self.unit_price
        except:
            return 0 
    
    def save(self, *args,**kargs):
        self.subtotal_budget = self.subtotal()
        super().save(*args,**kargs)

        if self.budget_id:
            self.budget.update_total()
    def __str__(self):
        return f'Orçamento: {self.budget.code} - Titulo: {self.budget.title} - Serviço: {self.service}'

class Material(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='materials')

    name = models.CharField(max_length=100, verbose_name='Material')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Quantidade', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário", null=True, blank=True)
    subtotal_material = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Subtotal')

    def subtotal(self):
        try:
            return self.quantity * self.unit_price
        except:
            return 0

    def save(self, *args, **kwargs):
        self.subtotal_material = self.subtotal()
        super().save(*args, **kwargs)

        # Atualiza total do orçamento
        if self.budget_id:
            self.budget.update_total()

    def __str__(self):
        return f"{self.name} ({self.budget.code})"

@receiver(post_save, sender=Budget)
def update_created_budgets_on_create(sender, instance, created, **kwargs):
    if created:  # só conta se for novo
        profile, _ = UserProfile.objects.get_or_create(user=instance.user)
        profile.created_budgets += 1
        profile.save()


    




from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.utils import timezone

class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    obs = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} {self.lastname} '

class Budget(models.Model):
    STATUS_CHOICES = [
        ('pendente',"Pendente"),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado')

    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=20,unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
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
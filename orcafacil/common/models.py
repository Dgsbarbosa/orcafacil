# common/models.py
from django.db import models
from datetime import timezone
class AddressMixin(models.Model):
    street = models.CharField(max_length=255, verbose_name="Endereço", null=True, blank=True)
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
        formatted_address = f" {self.street}, {self.number}, {self.complement}, {self.neighborhood}, {self.city}, {self.state}, {self.zipcode}"
        return formatted_address

class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de exclusão")

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])
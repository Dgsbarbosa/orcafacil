# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from .plans import PLAN_FEATURES

# ----------------------
# Gerenciador de usuário
# ----------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email deve ser fornecido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ----------------------
# Modelo CustomUser
# ----------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    accept_email = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# ----------------------
# Planos
# ----------------------
class Plan(models.TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    MASTER = 'master','Master'

# ----------------------
# Perfil do usuário
# ----------------------
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.FREE)
  
    address = models.TextField(blank=True, null=True)
    created_budgets = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f'{self.user.email} ({self.plan})'

    def can_create_budget(self):
        if self.plan == Plan.FREE and self.created_budgets >= 3:
            return False
        return True

    def features(self):
        return PLAN_FEATURES.get(self.plan, PLAN_FEATURES['free'])

# ----------------------
# Empresa
# ----------------------
class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    slogan = models.TextField(blank=True, null=True)

    def has_logo(self):
        return getattr(self.user.userprofile, 'plan', Plan.FREE) in [Plan.PRO, Plan.MASTER] and bool(self.logo)
    
    def has_slogan(self):
        return getattr(self.user.userprofile, 'plan', Plan.FREE) == Plan.MASTER and bool(self.slogan)

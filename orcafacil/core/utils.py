from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import Budget
from datetime import datetime
from accounts.models import CustomUser
from core.models import Client, Budget
from django.utils import timezone
import random


def count_budgets_per_month(user):
    
    date = datetime.now()
   
    budgets = Budget.objects.filter(user_id=user,  created_at__year=date.year, created_at__month=date.month)

    return budgets

def pass_rate(passed_value, total_value):
    """
    Calcula a taxa de aprovação ou sucesso em percentual.
    
    :param passed_value: quantidade ou valor que foi aprovado/sucesso
    :param total_value: quantidade ou valor total
    :return: percentual de aprovação (float)
    """
    if total_value == 0:
        return 0
    
    total = (passed_value / total_value) * 100 

    print( passed_value, total_value, total)
    return round(total)


def convert_in_brazilian_money(float_value):
    formatted_value = f"R$ {float_value:,.2f}".replace(',','X').replace('.',",").replace('X','.')

    return formatted_value
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import Budget
from datetime import datetime
from accounts.models import CustomUser
from core.models import Client, Budget
from django.utils import timezone
import random
# core/utils.py
from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone
from core.models import Budget

def normalize_budget_codes(batch_size: int = 500):
    """
    Normaliza o campo `code` de todos os Budgets para o padrão NNN-YYYY,
    reiniciando a contagem por usuário a cada ano.

    Retorna a quantidade de registros atualizados.
    """
    qs = Budget.objects.select_related('user').order_by('user_id', 'created_at').all()

    counter = {}   # chave: (user_id, year) -> contador atual
    to_update = [] # lista de objetos Budget para atualizar via bulk_update
    updated = 0

    for b in qs:
        if not b.created_at:
            # Se preferir, altere para usar outro campo ou setar a created_at para now()
            print(f"Aviso: Budget id={b.id} sem created_at — pulando.")
            continue

        year = b.created_at.year
        key = (b.user_id, year)

        # incrementa contador por (usuário, ano)
        current = counter.get(key, 0) + 1
        counter[key] = current

        new_code = f"{current:03d}-{year}"

        if b.code != new_code:
            b.code = new_code
            to_update.append(b)

        # Persistir em lotes
        if len(to_update) >= batch_size:
            try:
                with transaction.atomic():
                    Budget.objects.bulk_update(to_update, ['code'])
                updated += len(to_update)
                print(f"Persistidos {len(to_update)} registros... total atualizado: {updated}")
                to_update = []
            except Exception as e:
                print("Erro ao dar bulk_update (lote). Abortando. Erro:", e)
                raise

    # Persiste o restante
    if to_update:
        try:
            with transaction.atomic():
                Budget.objects.bulk_update(to_update, ['code'])
            updated += len(to_update)
            print(f"Persistidos {len(to_update)} registros (final).")
        except Exception as e:
            raise

    print(f"Concluído. Total de orçamentos atualizados: {updated}")
    return updated


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
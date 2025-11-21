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
# accounts/utils.py
from accounts.models import UserProfile,CustomUser
from core.models import Budget
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import base64

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io

def apply_watermark_footer_header(original_pdf_bytes, plan, company_name):
    reader = PdfReader(io.BytesIO(original_pdf_bytes))
    writer = PdfWriter()

                # Dados comuns

    width, height = A4  # 595 × 842 pt
    height_mark = 90
    position_header = height - 100
    position_footer = 10
    
    empresa = "Novo Padrão Reforma e Manutenção Predial"
    cnpj = "CNPJ 37.763.872/0001-11"
    tel1 = "+55 (14) 99734-9757"
    tel2 = "+55 (14) 99198-0130"
    email = "novopadrao.reformas@gmail.com"
    facebook = "https://www.facebook.com/novopadrao.reformas/"

    # Ícones
    facebook_icon = "core/static/core/images/facebook.png"
    whatsapp_icon = "core/static/core/images/whatsapp.png"
    email_icon = "core/static/core/images/email.png"

    for page_num in range(len(reader.pages)):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)

        
        # =======================
        # HEADER (somente PRO)
        # =======================
        if plan == "pro":
            can.setFont("Helvetica-Bold", 11)
            can.drawCentredString(width/2, height - 30, company_name)
            y = 55
            can.setFont("Helvetica", 8)

            can.drawString(25, y, empresa)
            can.drawString(25, y - 12, cnpj)

            # Telefones com ícone de WhatsApp
            try:
                can.drawImage(ImageReader(whatsapp_icon), 25, y - 32, width=10, height=10, mask="auto")
                can.drawString(40, y - 30, tel1)

                can.drawImage(ImageReader(whatsapp_icon), 25, y - 46, width=10, height=10, mask="auto")
                can.drawString(40, y - 44, tel2)
            except:
                can.drawString(25, y - 30, tel1)
                can.drawString(25, y - 44, tel2)
        
        else:
            try:
                can.drawImage(
                    ImageReader("core/static/core/images/marca_dagua.png"),
                    0, position_header,
                    width=width, height=height_mark,
                    mask="auto"
                )
            except:
                pass
       
        # =======================
        # FOOTER (PRO / FREE)
        # =======================

        # Linha superior
        can.setLineWidth(0.5)
        can.setStrokeColorRGB(0.8, 0.8, 0.8)
        can.line(20, 70, width - 20, 70)



        # =======================
        # Footer PRO
        # =======================
        if plan == "pro":
            y = 55
            can.setFont("Helvetica", 8)

            can.drawString(25, y, empresa)
            can.drawString(25, y - 12, cnpj)

            # Telefones com ícone de WhatsApp
            try:
                can.drawImage(ImageReader(whatsapp_icon), 25, y - 32, width=10, height=10, mask="auto")
                can.drawString(40, y - 30, tel1)

                can.drawImage(ImageReader(whatsapp_icon), 25, y - 46, width=10, height=10, mask="auto")
                can.drawString(40, y - 44, tel2)
            except:
                can.drawString(25, y - 30, tel1)
                can.drawString(25, y - 44, tel2)
            
           
            # Facebook ícone + link
            try:
                can.drawImage(ImageReader(facebook_icon), 250, y-12, width=10, height=10, mask="auto")
                can.drawString(265, y -12 , facebook)
            except:
                can.drawString(250, y - 30, facebook)

             # email
            try:
                can.drawImage(ImageReader(email_icon),250,y-44,width=10,height=10)
                can.drawString(265, y - 44, email)

            except:
                can.drawString(245, y - 44, email)
        # =======================
        # Footer FREE
        # =======================
        else:
            can.saveState()

            # Marca d’água no rodapé
            try:
                can.drawImage(
                    ImageReader("core/static/core/images/marca_dagua.png"),
                    0, position_footer,
                    width=width, height=height_mark,
                    mask="auto"
                )
            except:
                pass

            can.restoreState()

            # Texto com baixa opacidade
            

           

        can.save()
        packet.seek(0)

        overlay = PdfReader(packet)
        page = reader.pages[page_num]
        
        page.merge_page(overlay.pages[0])

        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def atualizar_created_budgets():
    """
    Atualiza o campo 'created_budgets' de todos os perfis de usuário
    com base na contagem real de orçamentos existentes.
    """
    users = CustomUser.objects.all()
    for user in users:
        perfil = UserProfile.objects.create(user=user)
        perfil.save()
        print(f"usuario criado: {user}")

    perfis = UserProfile.objects.all()
    total = perfis.count()
    atualizados = 0

    for profile in perfis:
        count = Budget.objects.filter(user=profile.user).count()
        if profile.created_budgets != count:
            profile.created_budgets = count
            profile.save()
            atualizados += 1

    print(f"✅ {atualizados}/{total} perfis atualizados com sucesso.")

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






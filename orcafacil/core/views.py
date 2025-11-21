# IMPORTAÇÕES
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string
from accounts.models import Company, UserProfile
from .models import Budget, Client,Services,Material
from .forms import ClientForm, BudgetForm, ServiceFormSet,MaterialFormSet
from .utils import count_budgets_per_month,pass_rate,atualizar_created_budgets, apply_watermark_footer_header
from django.template.loader import render_to_string
from django.db.models import Q, Sum
from django.contrib import messages
from accounts.forms import UserProfileForm, CompanyForm, LoginForm,CustomUserForm,CustomUserEditForm
from django.forms import inlineformset_factory

from .utils import normalize_budget_codes
import asyncio
from playwright.sync_api import sync_playwright
@login_required
def dashboard(request):
    user = request.user

    context = {
        'user':user
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def dashboard_content(request, section):
    """Retorna HTML parcial para cada seção"""

    
    context = {}
    user = request.user


    if section == 'home':


        context['user'] = user    
        context['count_clients'] = Client.objects.filter(user_id=user.id).count()
        context['count_budgets'] = Budget.objects.filter(user_id=user.id).count()
        context['count_pending_budgets'] = Budget.objects.filter(user_id=user.id,status="pendente").count()

       
        context['count_budget_datas'] = count_budgets_per_month(user)
        
        # Total de orçamentos do usuário
        total_budgets = Budget.objects.filter(user=user).count()

        # Total de orçamentos aprovados
        approved_budgets = Budget.objects.filter(user=user, status='aprovado').count()
        

        context['pass_rate'] = pass_rate(approved_budgets,total_budgets)
        
        context['budgets'] = Budget.objects.filter(user=user)[:10]
        
        
        
        html = render(request, 'core/home.html', context).content.decode('utf-8')
    
    elif section == 'clients':

        clients = Client.objects.filter(user=user,is_active=True)
        
        

        html = render(request, 'core/clients.html', context).content.decode('utf-8')
        
    elif section == 'client_form': 
        form_client = ClientForm()
        context['form_client'] = form_client
        html = render(request, 'core/client_form.html', context).content.decode('utf-8')
    
    elif section == 'budgets':
        html = render(request, 'core/budgets.html', context).content.decode('utf-8')
    
    elif section == "budget_form":
        clients = Client.objects.filter(user=request.user,is_active=True)

        # 🔹 Passa o user para o form (caso o BudgetForm use ele para filtrar clientes)
        budget_form = BudgetForm(user=request.user)

        # 🔹 Formset de serviços (vários por orçamento)
        formset = ServiceFormSet(prefix='services')

        materials_form = MaterialFormSet(prefix='materials')
        # 🔹 Adiciona no contexto
        context['budget_form'] = budget_form
        context['services_form'] = formset

        context['clients'] = clients
        context['materials_form']=materials_form

        
        html = render(request, 'core/budget_form.html', context).content.decode('utf-8')
    
    elif section == 'profile':

        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        company, _ = Company.objects.get_or_create(user=user)
        formAccess = CustomUserEditForm(instance=user)
        formProfile = UserProfileForm(instance=profile)
        formCompany = CompanyForm(instance=company)
        context['user']=user
        context['formAccess']=formAccess
        context['formProfile']=formProfile
        context['formCompany']=formCompany


        html = render(request, 'core/profile.html', context).content.decode('utf-8')
    
    else:
        html = "<p>Seção não encontrada.</p>"

    return JsonResponse({'html': html})


@login_required
def client_list(request):
    user = request.user

    # Pega parâmetros de query
    search = request.GET.get('search', '')        # busca por nome ou sobrenome
    status = request.GET.get('status', '')        # pendente, aprovado, recusado

    clients = Client.objects.filter(user=user,is_active=True).order_by('-created_at')

    # Filtra pelo termo
    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(lastname__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    # Filtra pelo status relacionado ao orçamento
    if status:
        clients = clients.filter(status=status).distinct()
        
        print(clients)
        
    context = {'clients': clients}
    html = render(request, 'core/clients_table.html', context).content.decode('utf-8')
    return JsonResponse({'html': html})


@login_required
def client_create(request):

    user = request.user
    if request.method ==  "POST":

        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user_id = user.id
            
            form.save()

            messages.success(request, f"Cliente {client} adicionado com Sucesso")
        

        else:
            messages.error(request, f"ERROR: {form.errors.as_text()}")


    return redirect("/core/")

@login_required
def client_view(request,client_id):


    client = get_object_or_404(Client, pk=client_id)

    context = {
        'client': client,

    }
    html = render_to_string('core/client_view.html', 
    context, request=request)
    return JsonResponse({'html': html})

@login_required
def client_edit(request, client_id):
    
    client = get_object_or_404(Client, pk=client_id)

    

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        
        
        if form.is_valid():
            form.save() 
            

            messages.success(request,"Cliente atualizado com sucesso")
        else:
            messages.error(request,f"{form.errors.as_text()}")
            print(form.errors.as_text())
        
        return redirect('/core')

    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client_id':client_id
        }
    html = render_to_string('core/client_edit.html', context, request=request)
    return JsonResponse({'html': html})

@login_required
def delete_client(request, client_id):
    if request.method == "POST":
        client = get_object_or_404(Client, id=client_id)
        try:
            client.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

@login_required
def budgets(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        budgets = Budget.objects.filter(user=request.user,is_active=True).order_by('-code')
        
        if search:
            budgets = budgets.filter(
                Q(code__icontains=search) |
                Q(client__name__icontains=search) |
                Q(status__icontains=search) |
                Q(created_at__icontains=search)
                
            )
        if status:
            budgets = budgets.filter(status__icontains=status)

        html = render_to_string('core/budgets_table.html', {'budgets': budgets})
        return JsonResponse({'html': html})
    
    html = render_to_string('core/budgets.html', {})
    return JsonResponse({'html': html})


@login_required
def budget_create(request):

    user = request.user
    
    if request.method == "POST":
        
        form = BudgetForm(request.POST)
        formset = ServiceFormSet(request.POST,prefix='services')
        material_formset = MaterialFormSet(request.POST, prefix='materials') 

        print('Validando Formulário...')

        if form.is_valid() and formset.is_valid() and material_formset.is_valid():
            budget = form.save(commit=False)
            
            budget.user = user 
            
            print("Salvando Formulário...")
            
            budget.save()

            services = formset.save(commit=False)

            material = material_formset.save(commit=False)

            for s in services:
                s.budget = budget
                s.save()
              
            for m in material_formset.save(commit=False):
                m.budget = budget
                m.save()

            formset.save_m2m()
            material_formset.save_m2m()

            print("Orçamento criado com sucesso.")

            messages.success(request, "Orçamento gravado com sucesso")
        
        else:

            print("Houve erros de validação.")
            print("Form errors:", form.errors.as_text())
            print("Formset non-form errors:", formset.non_form_errors())
            print("Formset management form errors:", formset.management_form.errors)
            print("Formset individual form errors:", [f.errors for f in formset])

            # 🧩 MENSAGENS PARA O USUÁRIO
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro em {field}: {error}")

            if formset.management_form.errors:
                for field, errors in formset.management_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no formset ({field}): {error}")

            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(request, f"Erro geral nos serviços: {error}")

            for i, f in enumerate(formset.forms):
                if f.errors:
                    for field, errors in f.errors.items():
                        for error in errors:
                            messages.error(request, f"Serviço {i + 1} - {field}: {error}")


    return redirect('/core')

@login_required
def budget_view(request, budget_id):

    budget = get_object_or_404(Budget, pk=budget_id)

    print(len(budget.services.all()))
    context = {
        'budget':budget
    }
    html = render(request, "core/budget_view.html",context).content.decode('utf-8')

    return JsonResponse({"html":html})

@login_required
def budget_edit(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    prefix = 'services'   
    extra = 0
    if len(budget.services.all()) == 0:
        extra = 1
    ServiceFormSetEdit = inlineformset_factory(
        Budget,
        Services,
        form=ServiceFormSet.form,  # usa o mesmo form
        extra=extra ,                   # sem formulário vazio
        can_delete=True
    )

    extra_material = 0
    if len(budget.materials.all() )== 0:
        extra_material = 1
    MaterialFormSetEdit = inlineformset_factory(Budget, Material, form=MaterialFormSet.form, extra=extra_material, can_delete=True)
    
    if request.method == 'POST':
        # cria os forms com instance e prefix corretos
        form = BudgetForm(request.POST, instance=budget)
        formset = ServiceFormSetEdit(request.POST, instance=budget, prefix=prefix)
        material_formset = MaterialFormSetEdit(request.POST, instance=budget, prefix='materials')

        

        # debug (remova em produção)
        print('\n>>> POST - Validando Formulários..\n')
        
        if form.is_valid() and formset.is_valid() and material_formset.is_valid():
            # salva orçamento
            
            print("Formulários validados...\n")
            budget = form.save(commit=False)

              # mantém dono
            budget.save()

            
            # salva serviços (novos e editados)
            services_objs = formset.save(commit=False)
            for s in services_objs:
                s.budget = budget

                print(f"{'-'*40}\n{s} ")
                s.save()
            for m in material_formset.save(commit=False):
                m.budget = budget
                m.save()
            # deleta itens marcados com DELETE
            for obj in formset.deleted_objects:
                obj.delete()
            for obj in material_formset.deleted_objects:
                obj.delete()
            # finalize formset m2m (não estritamente necessário para FK simples)

            formset.save_m2m()

            # atualiza total
            budget.update_total()

            messages.success(request, "Orçamento atualizado com sucesso!")

            # Como você usa AJAX para carregar a tela, retorne o HTML atualizado
            return redirect("/core")
        
        else:
            # se inválido, re-renderiza o formulário com erros e devolve para o front
          
            messages.error(request,"ERRO: Não foi posivel salvar o orçamento")
            
            print("\n❌ ERROS DE VALIDAÇÃO ❌\n")
            print("→ Form errors:")
            print(form.errors.as_json())
            messages.error(request,form.errors.as_text())
            print("\n→ Formset errors:")
            for i, f in enumerate(formset.forms):
                if f.errors:
                    print(f"Serviço {i}: {f.errors}")
                    messages.error(request,f'Erro: {f.errors.as_text()}')
            print("\n→ Non-form errors:", formset.non_form_errors())
            print("→ Management form errors:", formset.management_form.errors)


            return redirect('/core')
    
    else:
        # GET — apenas monta os forms para exibir
        form = BudgetForm(instance=budget)
        formset = ServiceFormSetEdit(instance=budget, prefix=prefix)

        material_formset = MaterialFormSetEdit(instance=budget, prefix='materials')
        context = {
            'form': form,
            'formset': formset,
            'budget': budget,
            'materials_formset': material_formset,
        }
        html = render(request, 'core/budget_edit.html', context).content.decode('utf-8')
        return JsonResponse({'success': True, 'html': html})


@login_required
def budget_delete(request, budget_id):


    try:
        budget = get_object_or_404(Budget, pk=budget_id)
        
        response = {"success":"success"}
        budget.delete()

        messages.success(request,"Orçamento deletado com sucesso")
        
    except:
        messages.error(request,"Ocorreu um erro ao deletar o orçamento")
        response = {"error":"ERROR"}
    
    return  JsonResponse(response)

@login_required
def view_report(request,pk):

    budget = get_object_or_404(Budget, id=pk)
    services = budget.services.all()
    materials = budget.materials.all()

    # Calcule o total dos serviços
    total_services = budget.services.aggregate(total=Sum("subtotal_services"))['total'] or 0

    # Calcule o total dos materiais
    total_materials = budget.materials.aggregate(total=Sum("subtotal_material"))['total'] or 0
    
    context = {
        "budget": budget,
        "services": services,
        "materials": materials,
        "total_services":total_services,
        "total_materials":total_materials
    }

    # print(request.user.userprofile.plan)

    return render(request, "core/report.html", context)
    


@login_required
def download_report(request, pk):
    budget = get_object_or_404(Budget, id=pk)

    # Coleta de dados
    services = budget.services.all()
    materials = budget.materials.all()

    total_services = budget.services.aggregate(total=Sum("subtotal_services"))["total"] or 0
    total_materials = budget.materials.aggregate(total=Sum("subtotal_material"))["total"] or 0

    profile = request.user.userprofile
    plan = profile.plan  # "free" ou "pro"
    marca_dagua_base64 = "data:image/png;base64,AAAA...."

    # Escolhe header e footer
    if plan == "pro":
        header_html = f"""
        <div class="header" style="font-size:12px; text-align:center; width:100%; padding:4px 0;">
            <b>{request.user.company.company_name}</b>
        </div>
        """

        footer_html = """
        <div class="footer" style="font-size:10px; text-align:center; width:100%; padding:6px 0;
            border-top:1px solid #ccc;">
            Facebook: novopadrao.reformas • Instagram: @novopadrao.reformas — Obrigado pela confiança!
        </div>
        """
    else:
        header_html = """
        <div class="header" style="height:20px;"></div>
        """

        footer_html = f"""
        <div class="footer" style="text-align:center; width:100%; padding:10px 0;">
            <img src="{marca_dagua_base64}" style="width:100px; opacity:0.15;" />
        </div>
        """

    # Renderiza o HTML da página que será convertida
    html = render_to_string("core/pdf_template.html", {
        "budget": budget,
        "services": services,
        "materials": materials,
        "total_services": total_services,
        "total_materials": total_materials,
        "plan": plan,
        "user": request.user,
    })

    # Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.set_content(html, wait_until="networkidle")

        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "20px", "bottom": "20px", "left": "10mm", "right": "10mm"},
            display_header_footer=False
        )

        browser.close()

        final_pdf = apply_watermark_footer_header(
        pdf_bytes,
        plan=plan,
        company_name=request.user.company.company_name
    )

    response = HttpResponse(final_pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=Orcamento-{budget.code}.pdf"
    return response


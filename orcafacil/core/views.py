from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from .models import Budget, Client
from .forms import ClientForm, BudgetForm, ServiceFormSet
from .utils import count_budgets_per_month,pass_rate
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib import messages


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

    elif section == 'profile':
        html = render(request, 'core/profile.html', context).content.decode('utf-8')
    elif section == 'budgets':
        html = render(request, 'core/budgets.html', context).content.decode('utf-8')
    elif section == 'clients':

        clients = Client.objects.filter(user=user)
        
        # context['clients'] = 

        html = render(request, 'core/clients.html', context).content.decode('utf-8')
        
    elif section == 'client_form': 
        form_client = ClientForm()
        context['form_client'] = form_client
        html = render(request, 'core/client_form.html', context).content.decode('utf-8')

    elif section == "budget_form":
        clients = Client.objects.filter(user=request.user)

        # 🔹 Passa o user para o form (caso o BudgetForm use ele para filtrar clientes)
        budget_form = BudgetForm(user=request.user)

        # 🔹 Formset de serviços (vários por orçamento)
        formset = ServiceFormSet(prefix='services')

        # 🔹 Adiciona no contexto
        context['budget_form'] = budget_form
        context['services_form'] = ServiceFormSet(prefix='services')

        context['clients'] = clients

        
        html = render(request, 'core/budget_form.html', context).content.decode('utf-8')
    else:
        html = "<p>Seção não encontrada.</p>"

    return JsonResponse({'html': html})


@login_required
def client_list(request):
    user = request.user

    # Pega parâmetros de query
    search = request.GET.get('search', '')        # busca por nome ou sobrenome
    status = request.GET.get('status', '')        # pendente, aprovado, recusado

    clients = Client.objects.filter(user=user)

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
        budgets = Budget.objects.all()

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
def budget_list(request):
    return render(request, 'core/budget_list.html')

@login_required
def budget_create(request):

    user = request.user
    
    if request.method == "POST":
        
        form = BudgetForm(request.POST)
        formset = ServiceFormSet(request.POST,prefix='services')


        print("Antes if is_valid()")
        print(formset)

        if form.is_valid() and formset.is_valid():
            budget = form.save(commit=False)
            
            budget.user = user 

            # print(budget)
            # print("----------")

            budget.save()

            services = formset.save(commit=False)

            for s in services:
                s.budget = budget
                s.save()
              

            formset.save_m2m()

            messages.success(request, "Orçamento gravado com sucesso")
        
        else:

            print("Entrou no else — houve erros de validação.")
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

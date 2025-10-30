from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from .models import Budget, Client
from .forms import ClientForm, BudgetForm
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
        clients = Client.objects.filter(user_id = user)
        budget_form = BudgetForm(user=user)
        context['budget_form'] = budget_form
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
    print("teste")
    return JsonResponse({"teste":"teste"})

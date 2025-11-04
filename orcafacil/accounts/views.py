from django.shortcuts import render,redirect
from .models import UserProfile
from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from .forms import CustomUserForm, LoginForm, CustomUserEditForm

def login_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request,user)
            messages.success(request,"Login realizado com sucesso")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Usuários e/ou senha inválidas")
   

    context = {
        
    }

    return render(request, 'accounts/login.html',context)

def logout_view(request):

    return render(request, 'accounts/logout.html')

def register_view(request):

    if request.method == 'POST':

        form = CustomUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)

            user.save()

            messages.success(request, "Cadastro realizado com sucesso")

            return redirect(reverse_lazy('accounts:login'))

        else:
            errors = form.errors.as_data()
            
            for field, error in errors.items():
                for e in error:
                    messages.error(request,f"{field}: {e}")
                    print(error)
            print(errors)
            # messages.error(request,"")
        


    form = CustomUserForm()

    context = {
        'form':form
    }

    return render(request, 'accounts/register.html', context)

def profile_view(request):
    return render(request, 'accounts/profile.html')

def upgrade_plan(request):
    return render(request, 'accounts/upgrade.html')


def edit_access(request):

    user = request.user

    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=user)
        
        if form.is_valid():

            form.save()
            messages.success(request," Teste")
        else:
            errors = form.errors.as_text()
            messages.error(request,f"Erro: {errors}")
    else:
        print("error")        
    return redirect("/core")

def edit_profile(request):

    pass

def edit_company(request):

    pass


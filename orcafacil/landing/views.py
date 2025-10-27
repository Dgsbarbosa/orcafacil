from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import logout


# Create your views here.

def home(request):
    
   
    
    context = {
        "teste":"olha a mensagem que escrevi",
    }
    return render(request,"home.html",context)
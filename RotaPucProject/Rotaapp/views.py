from django.shortcuts import render
import requests

def home(request):
    return render(request, 'Pedro/html-paginas-pedro/index.html')

def universidades(request):
    return render(request, 'Pedro/html-paginas-pedro/index2.html')

def paises(request):
    return render(request, 'Manu/html-paginas-manu/paises.html')

def contatos(request):
    return render(request, 'Daniel/html-paginas-daniel/contatos.html')

def nova_pergunta(request):
    return render(request, 'Daniel/html-paginas-daniel/nova-pergunta.html')

def quem_somos(request):
    return render(request, 'Pedro/html-paginas-pedro/index3.html')

def processo_seletivo(request):
    return render(request, 'Pedro/html-paginas-pedro/index4.html')
from django.shortcuts import render

def home(request):
    return render(request, 'Pedro/html-paginas-pedro/index.html')


def paises(request):
    return render(request, 'Manu/html-paginas-manu/paises.html')

def contatos(request):
    return render(request, 'Daniel/html-paginas-daniel/contatos.html')

def nova_pergunta(request):
    return render(request, 'Daniel/html-paginas-daniel/nova-pergunta.html')

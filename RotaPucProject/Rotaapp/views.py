from django.shortcuts import render

def home(request):
    return render(request, 'Pedro/html-paginas-pedro/index.html')
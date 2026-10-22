from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pais, Universidade, Pergunta
from .forms import PerguntaForm


def home(request):
    # "-continente" ordena de Z a A, para Europa aparecer antes de América do Sul
    paises = Pais.objects.order_by("-continente", "nome")
    return render(request, 'Pedro/html-paginas-pedro/index.html', {'paises': paises})


def universidades(request):
    paises = Pais.objects.all()
    total_universidades = Universidade.objects.count()
    return render(request, 'Pedro/html-paginas-pedro/index2.html', {
        'paises': paises,
        'total_universidades': total_universidades,
    })


def paises(request):
    paises = Pais.objects.order_by("-continente", "nome")
    return render(request, 'Manu/html-paginas-manu/paises.html', {'paises': paises})


def contatos(request):
    return render(request, 'Daniel/html-paginas-daniel/contatos.html')


def nova_pergunta(request):
    if request.method == 'POST':
        # Formulário enviado: preenche o form com o que o usuário digitou
        form = PerguntaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sua pergunta foi postada!')
            return redirect('nova_pergunta')
    else:
        # Acesso normal à página: formulário vazio
        form = PerguntaForm()

    perguntas = Pergunta.objects.order_by('-data_criacao')[:5]
    return render(request, 'Daniel/html-paginas-daniel/nova-pergunta.html', {
        'form': form,
        'perguntas': perguntas,
    })


def quem_somos(request):
    return render(request, 'Pedro/html-paginas-pedro/index3.html')


def processo_seletivo(request):
    return render(request, 'Pedro/html-paginas-pedro/index4.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Pais, Universidade, Pergunta, NotaDeCorte, PreRequisito, EtapaProcesso, PaginaInstitucional,
)
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
    # .first() devolve None se o texto ainda não foi cadastrado (o template mostra um aviso)
    pagina = PaginaInstitucional.objects.filter(slug="quem-somos").first()
    return render(request, 'Pedro/html-paginas-pedro/index3.html', {'pagina': pagina})


def processo_seletivo(request):
    # Mostra só a lista de CR do semestre mais recente cadastrado
    semestre = NotaDeCorte.objects.order_by("-semestre").values_list("semestre", flat=True).first()
    notas = list(NotaDeCorte.objects.filter(semestre=semestre))
    # A tabela da página é dividida em colunas de 4 departamentos cada
    colunas_cr = [notas[i:i + 4] for i in range(0, len(notas), 4)]

    return render(request, 'Pedro/html-paginas-pedro/index4.html', {
        'semestre': semestre,
        'colunas_cr': colunas_cr,
        'pre_requisitos': PreRequisito.objects.all(),
        # prefetch_related busca os blocos de todos os passos de uma vez só
        'etapas': EtapaProcesso.objects.prefetch_related("blocos"),
    })
    
def forum(request):
    return render(request, 'Manu/html-paginas-manu/forum.html')

def universidade(request, id):
    universidade = get_object_or_404(Universidade, id=id)
    programas = universidade.programas.all()
    return render(request, 'Manu/html-paginas-manu/universidade.html', {
        'universidade': universidade,
        'programas': programas,
    })
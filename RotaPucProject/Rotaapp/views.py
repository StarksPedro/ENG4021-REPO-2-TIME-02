from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import (
    Pais, Universidade, Pergunta, NotaDeCorte, PreRequisito, EtapaProcesso, PaginaInstitucional,
)
from .forms import PerguntaForm, RespostaForm, CadastroForm
from .context_processors import separar_linhas, dados_do_contato
from .cotacao import buscar_cotacao
from .notas_corte import checar_se_necessario
from django.db.models import Count


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
    # Filtros vêm na URL (ex.: /paises/?continente=Europa&lingua=Alemão)
    busca = request.GET.get('busca', '').strip()
    continente = request.GET.get('continente', '')
    lingua = request.GET.get('lingua', '')

    paises = Pais.objects.order_by("-continente", "nome")
    # Cada filtro só é aplicado se o usuário escolheu algo
    if busca:
        paises = paises.filter(nome__icontains=busca)
    if continente:
        paises = paises.filter(continente=continente)
    if lingua:
        paises = paises.filter(idioma_oficial=lingua)

    return render(request, 'Manu/html-paginas-manu/paises.html', {
        'paises': paises,
        # As opções dos selects saem do próprio banco, sem repetir valores,
        # para sempre baterem com o que está cadastrado (ex.: "América do Sul" com acento)
        'continentes': Pais.objects.order_by('continente').values_list('continente', flat=True).distinct(),
        'linguas': Pais.objects.order_by('idioma_oficial').values_list('idioma_oficial', flat=True).distinct(),
        'busca': busca,
        'continente': continente,
        'lingua': lingua,
    })


def contatos(request):
    # Os dados vêm do modelo ContatoCoordenacao (cadastrado no /admin).
    # A função dados_do_contato fica em context_processors.py porque o rodapé usa a mesma lógica.
    contexto = dados_do_contato()
    return render(request, 'Daniel/html-paginas-daniel/contatos.html', contexto)


@login_required  # só quem está logado pode perguntar; os outros vão para a tela de login
def nova_pergunta(request):
    if request.method == 'POST':
        # Formulário enviado: preenche o form com o que o usuário digitou
        form = PerguntaForm(request.POST)
        if form.is_valid():
            # commit=False cria a pergunta sem salvar ainda, para preencher o autor antes
            pergunta = form.save(commit=False)
            pergunta.autor = request.user.get_full_name() or request.user.username
            pergunta.save()
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
    # A cada visita só confere uma data; se já passou o intervalo, atualiza em segundo plano
    checar_se_necessario()
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
    # Perguntas mais novas primeiro, já com o total de respostas de cada uma
    perguntas = Pergunta.objects.annotate(total_respostas=Count('respostas')).order_by('-data_criacao')
    return render(request, 'Manu/html-paginas-manu/forum.html', {'perguntas': perguntas})
    
def discussao(request, id):
    pergunta = get_object_or_404(Pergunta, id=id)

    if request.method == 'POST':
        # Qualquer um pode LER a discussão, mas só quem está logado pode RESPONDER.
        # Por isso o login é conferido aqui, e não com @login_required na view inteira.
        if not request.user.is_authenticated:
            # ?next= faz a pessoa voltar para esta pergunta depois de entrar
            return redirect(f"{reverse('login')}?next={request.path}")

        form = RespostaForm(request.POST)
        if form.is_valid():
            # commit=False cria a resposta sem salvar ainda, para preencher a pergunta e o autor
            resposta = form.save(commit=False)
            resposta.pergunta = pergunta
            resposta.autor = request.user.get_full_name() or request.user.username
            resposta.save()
            messages.success(request, 'Sua resposta foi publicada!')
            # Redireciona para não reenviar a resposta se a pessoa apertar F5
            return redirect(reverse('discussao', args=[pergunta.id]) + '#respostas')
    else:
        form = RespostaForm()

    return render(request, 'Manu/html-paginas-manu/discussao.html', {
        'pergunta': pergunta,
        'respostas': pergunta.respostas.all(),
        'form': form,
    })


def pais(request, id):
    pais = get_object_or_404(Pais, id=id)
    return render(request, 'Manu/html-paginas-manu/pais.html', {
        'pais': pais,
        'universidades': pais.universidades.all(),
        'requisitos': separar_linhas(pais.requisitos_para_entrar),
        # Integração com API: cotação da moeda do país em reais (ver cotacao.py)
        'cotacao': buscar_cotacao(pais.codigo_moeda),
    })

def universidade(request, id):
    universidade = get_object_or_404(Universidade, id=id)

    def itens(tipo):
        # Textos de um tipo de item (requisito, certificado, custo, bolsa, documento), na ordem cadastrada
        return [item.texto for item in universidade.itens.filter(tipo=tipo)]

    return render(request, 'Manu/html-paginas-manu/universidade.html', {
        'universidade': universidade,
        'programas': universidade.programas.all(),
    })


# ===================== CADASTRO, LOGIN E LOGOUT =====================
# Usamos o sistema de usuários que já vem no Django (django.contrib.auth):
# a senha é guardada criptografada e o login fica salvo na sessão do navegador.
# O login e o logout usam as views prontas do Django (LoginView e LogoutView), ligadas em urls.py.
# Só o cadastro precisa de uma view nossa.

def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')  # quem já está logado não precisa se cadastrar

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()      # cria o usuário no banco (tabela auth_user)
            login(request, usuario)    # já deixa a pessoa logada depois de se cadastrar
            messages.success(request, f'Conta criada! Bem-vindo(a), {usuario.first_name}.')
            return redirect('home')
    else:
        form = CadastroForm()

    return render(request, 'Daniel/html-paginas-daniel/cadastro.html', {'form': form})

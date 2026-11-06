from .models import ContatoCoordenacao


def separar_linhas(texto):
    # Os campos do contato guardam um item por linha: "linha 1\nlinha 2" vira ["linha 1", "linha 2"]
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def dados_do_contato():
    # Busca o contato da coordenação no banco e já deixa tudo pronto para o template.
    # Usado pela página de Contatos (views.contatos) e pelo rodapé de todas as páginas.
    contato = ContatoCoordenacao.objects.first()  # None se ainda não foi cadastrado
    if contato is None:
        return {'contato': None}

    telefones = []
    for telefone in separar_linhas(contato.telefones):
        # Para o link "tel:" só servem os números: "+55 21 3527-1578" vira "+552135271578"
        numeros = "".join(caractere for caractere in telefone if caractere.isdigit())
        telefones.append({'texto': telefone, 'link': "+" + numeros})

    return {
        'contato': contato,
        'enderecos': separar_linhas(contato.endereco),
        'emails': separar_linhas(contato.emails),
        'telefones': telefones,
        'horarios': separar_linhas(contato.horario),
        # "@ccci.pucrio" vira o endereço do perfil no Instagram
        'instagram_link': "https://www.instagram.com/" + contato.instagram.lstrip("@") + "/",
    }


def rodape(request):
    # Context processor: o Django chama esta função em TODA página e coloca o que ela
    # devolve no context do template. Assim o rodapé do base (index5.html) recebe os
    # dados do banco sem precisar mexer na view de cada página.
    # Ele está registrado em settings.py, na lista TEMPLATES > OPTIONS > context_processors.
    return {'rodape': dados_do_contato()}

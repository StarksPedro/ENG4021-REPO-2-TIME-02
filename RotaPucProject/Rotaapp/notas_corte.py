"""Atualização automática das notas de corte a partir do PDF da CCCI/PUC-Rio.

Fluxo: baixa o PDF -> compara a "impressão digital" (hash) com a da última vez ->
se mudou, lê a tabela, valida e grava no banco. Se alguma coisa estiver estranha,
nada é gravado e o motivo fica em FonteNotasDeCorte.ultimo_resultado.
"""
import hashlib
import re
import threading
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.db import close_old_connections, transaction
from django.utils import timezone

from .models import FonteNotasDeCorte, NotaDeCorte

MINIMO_DEPARTAMENTOS = 20           # abaixo disso o PDF é considerado estranho
TIMEOUT_SEGUNDOS = 8                # tempo máximo esperando o servidor da PUC
ESPERA_APOS_TENTATIVA = timedelta(hours=1)   # não repetir tentativas em sequência
CABECALHOS = {"User-Agent": "Mozilla/5.0 (RotaPUC - projeto academico)"}

LINHA_NOTA = re.compile(r"^(?P<departamento>.+?)\s+(?P<nota>\d{1,2}[.,]\d{1,2})$")
SEMESTRE_NO_TEXTO = re.compile(r"Corte[^\n]*?(20\d{2}\.[12])")
SEMESTRE_NA_URL = re.compile(r"(20\d{2})\.([12])")


class ErroNotas(Exception):
    """O PDF foi baixado mas não parece a lista de CR esperada."""


class PdfNaoEncontrado(Exception):
    """O endereço não existe (ainda)."""


def baixar_pdf(url):
    import requests  # importado aqui para o site não cair se a biblioteca faltar

    resposta = requests.get(url, timeout=TIMEOUT_SEGUNDOS, headers=CABECALHOS)
    if resposta.status_code in (403, 404):
        raise PdfNaoEncontrado(f"{url} (HTTP {resposta.status_code})")
    resposta.raise_for_status()
    if not resposta.content.startswith(b"%PDF"):
        raise ErroNotas("O endereço não devolveu um PDF.")
    return resposta.content


def extrair_notas(conteudo, url=""):
    import pdfplumber

    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        texto = "\n".join((pagina.extract_text() or "") for pagina in pdf.pages)

    achou = SEMESTRE_NO_TEXTO.search(texto) or SEMESTRE_NA_URL.search(url)
    if not achou:
        raise ErroNotas("Não encontrei o semestre (ex.: 2026.2) no PDF.")
    semestre = achou.group(1) if achou.re is SEMESTRE_NO_TEXTO else f"{achou.group(1)}.{achou.group(2)}"

    notas = {}
    for linha in texto.splitlines():
        parte = LINHA_NOTA.match(linha.strip())
        if not parte:
            continue
        departamento = parte.group("departamento").strip()
        try:
            nota = Decimal(parte.group("nota").replace(",", "."))
        except InvalidOperation:
            continue
        if departamento in notas:
            raise ErroNotas(f"Departamento repetido no PDF: {departamento}")
        if not (Decimal("0") <= nota <= Decimal("10")):
            raise ErroNotas(f"Nota fora de 0 a 10 em {departamento}: {nota}")
        notas[departamento] = nota

    if len(notas) < MINIMO_DEPARTAMENTOS:
        raise ErroNotas(f"Só encontrei {len(notas)} departamentos (mínimo {MINIMO_DEPARTAMENTOS}).")
    return semestre, notas


def proxima_url(url):
    """2026.2 -> 2027.1 ; 2026.1 -> 2026.2 (supondo que o nome do arquivo siga o padrão)."""
    achou = SEMESTRE_NA_URL.search(url)
    if not achou:
        return None
    ano, parte = int(achou.group(1)), int(achou.group(2))
    novo = f"{ano}.2" if parte == 1 else f"{ano + 1}.1"
    return url[:achou.start()] + novo + url[achou.end():]


def _gravar(fonte, conteudo, url, agora):
    semestre, notas = extrair_notas(conteudo, url)
    with transaction.atomic():
        for departamento, nota in notas.items():
            NotaDeCorte.objects.update_or_create(
                departamento=departamento, semestre=semestre, defaults={"nota": nota}
            )
        NotaDeCorte.objects.filter(semestre=semestre).exclude(departamento__in=notas).delete()
    fonte.url = url
    fonte.hash_pdf = hashlib.sha256(conteudo).hexdigest()
    fonte.ultima_atualizacao = agora
    return f"{len(notas)} departamentos gravados para {semestre}."


def _verificar(fonte, forcar, agora):
    # 1) já saiu o PDF do próximo semestre?
    candidata = proxima_url(fonte.url)
    if candidata:
        try:
            conteudo = baixar_pdf(candidata)
        except Exception:
            conteudo = None  # não existe ainda (ou a rede falhou: o passo 2 acusa)
        if conteudo:
            return _gravar(fonte, conteudo, candidata, agora)

    # 2) o PDF atual mudou?
    conteudo = baixar_pdf(fonte.url)
    if not forcar and hashlib.sha256(conteudo).hexdigest() == fonte.hash_pdf:
        return "PDF igual ao da última vez, nada a atualizar."
    return _gravar(fonte, conteudo, fonte.url, agora)


def atualizar(fonte, forcar=False):
    """Roda uma checagem agora. Devolve a mensagem de resultado ou levanta o erro."""
    agora = timezone.now()
    fonte.ultima_tentativa = agora
    try:
        mensagem = _verificar(fonte, forcar, agora)
    except Exception as erro:
        fonte.ultimo_resultado = f"Falhou: {erro}"[:250]
        fonte.save()
        raise
    fonte.ultima_checagem_ok = agora
    fonte.ultimo_resultado = mensagem[:250]
    fonte.save()
    return mensagem


def _esta_na_hora(fonte, agora):
    if fonte.ultima_tentativa and agora - fonte.ultima_tentativa < ESPERA_APOS_TENTATIVA:
        return False
    if fonte.ultima_checagem_ok is None:
        return True
    return agora - fonte.ultima_checagem_ok >= timedelta(days=fonte.intervalo_dias)


def _executar(pk):
    try:
        atualizar(FonteNotasDeCorte.objects.get(pk=pk))
    except Exception:
        pass  # o motivo já ficou salvo em ultimo_resultado (aparece no /admin)
    finally:
        close_old_connections()


def checar_se_necessario(em_segundo_plano=True):
    """Chamada a cada visita à página. Quase sempre só confere uma data e sai."""
    fonte = FonteNotasDeCorte.obter()
    agora = timezone.now()
    if not _esta_na_hora(fonte, agora):
        return False
    # Reserva a checagem: se duas visitas chegarem juntas, só uma consegue trocar
    # ultima_tentativa e seguir adiante.
    reservou = FonteNotasDeCorte.objects.filter(
        pk=fonte.pk, ultima_tentativa=fonte.ultima_tentativa
    ).update(ultima_tentativa=agora)
    if not reservou:
        return False
    if em_segundo_plano:
        threading.Thread(target=_executar, args=(fonte.pk,), daemon=True).start()
    else:
        _executar(fonte.pk)
    return True
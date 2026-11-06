"""
Integração com a API de câmbio da AwesomeAPI (https://docs.awesomeapi.com.br/).

POR QUÊ: o estudante que vai fazer intercâmbio precisa saber quanto vale a moeda do
país de destino em reais para planejar o orçamento (aluguel, transporte, comida...).
Com a API, a cotação aparece sempre atualizada na página do país, sem ninguém precisar
cadastrar o valor à mão.

COMO: a view `pais` chama buscar_cotacao("EUR"). Esta função faz uma requisição GET para
https://economia.awesomeapi.com.br/json/last/EUR-BRL, que devolve um JSON assim:

    {"EURBRL": {"code": "EUR", "codein": "BRL", "name": "Euro/Real Brasileiro",
                "bid": "6.2135", "create_date": "2026-11-06 10:15:02", ...}}

"bid" é o valor de compra de 1 unidade da moeda em reais.
A API é gratuita e não precisa de cadastro (sem chave há um limite de requisições).
"""

import json
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.cache import cache

URL_API = "https://economia.awesomeapi.com.br/json/last/{codigo}-BRL"
TEMPO_LIMITE = 5          # segundos esperando a API responder antes de desistir
TEMPO_CACHE = 60 * 30     # guarda a cotação por 30 minutos


def buscar_cotacao(codigo_moeda):
    """Devolve um dicionário com a cotação da moeda em reais, ou None se não conseguir."""
    if not codigo_moeda:
        return None
    codigo_moeda = codigo_moeda.upper()

    # 1) Se a cotação foi buscada há menos de 30 minutos, usa a que está guardada no cache.
    #    Assim o site não chama a API a cada visita (fica mais rápido e não estoura o limite).
    chave_cache = f"cotacao-{codigo_moeda}"
    cotacao = cache.get(chave_cache)
    if cotacao:
        return cotacao

    # 2) Chama a API. Se ela estiver fora do ar, demorar mais de 5 segundos ou devolver algo
    #    inesperado, a função devolve None e a página mostra "cotação indisponível" em vez de quebrar.
    try:
        requisicao = Request(URL_API.format(codigo=codigo_moeda), headers={"User-Agent": "RotaPUC"})
        with urlopen(requisicao, timeout=TEMPO_LIMITE) as resposta:
            dados = json.load(resposta)

        item = dados[f"{codigo_moeda}BRL"]
        valor = float(item["bid"])
        cotacao = {
            "codigo": codigo_moeda,
            "nome": item["name"].split("/")[0],               # "Euro/Real Brasileiro" -> "Euro"
            "valor": valor,                                    # 1 EUR = 6.2135 reais
            "casas": 2 if valor >= 0.1 else 4,                 # moedas "baratas" (peso) precisam de mais casas
            "cem_reais": 100 / valor,                          # quanto R$ 100 valem nessa moeda
            "atualizado_em": datetime.strptime(item["create_date"], "%Y-%m-%d %H:%M:%S"),
        }
    except (URLError, TimeoutError, OSError, KeyError, ValueError, TypeError, ZeroDivisionError):
        return None

    cache.set(chave_cache, cotacao, TEMPO_CACHE)
    return cotacao

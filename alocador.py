# alocador.py
# Parte principal do projeto: divide o verde do semáforo usando Programação Dinâmica.
#
# O problema é uma "mochila de grupos":
#   - cada fase do semáforo é um grupo;
#   - os segundos que a fase pode receber são as opções do grupo;
#   - os 81 segundos de verde do ciclo são a capacidade da mochila.

import math
from dataclasses import dataclass
from functools import lru_cache


CICLO = 90          # duração do ciclo em segundos
PERDIDO = 3         # tempo perdido em cada fase (amarelo e vermelho geral)
VERDE_TOTAL = CICLO - PERDIDO * 3   # 90 - 9 = 81 segundos para dividir

LARGURA_TRAVESSIA_M = 12.3
VELOCIDADE_VULNERAVEL = 0.9   # m/s (idoso, PcD, carrinho de bebê)
TEMPO_REACAO = 3              # tempo para a pessoa perceber o verde e começar

# Tempo mínimo que um pedestre vulnerável precisa: ceil(13,67) + 3 = 17 s
TEMPO_MINIMO_TRAVESSIA = math.ceil(LARGURA_TRAVESSIA_M / VELOCIDADE_VULNERAVEL) + TEMPO_REACAO

EPS = 0.001         # custo pequeno por segundo, para não dar verde à toa
INVIAVEL = -math.inf

# Posição de cada fase nas listas de demandas e de verdes
PRINCIPAL = 0
PEDESTRES = 1
TRANSVERSAL = 2


@dataclass(frozen=True)
class Fase:
    nome: str
    taxa: float     # quantos são atendidos por segundo de verde
    minimo: int
    maximo: int
    peso: float
    base: int       # verde usado quando não há movimento especial


FASES = [
    Fase("Carros via principal", 1.0, 10, 60, 1.0, 36),
    Fase("Pedestres", 2.0, TEMPO_MINIMO_TRAVESSIA, 45, 2.0, TEMPO_MINIMO_TRAVESSIA),
    Fase("Carros via transversal", 0.5, 10, 60, 1.0, 28),
]


# Benefício de dar "segundos" de verde para uma fase.
# Só conta quem realmente é atendido.
def beneficio_fase(fase, demanda, segundos):
    return fase.peso * min(demanda, fase.taxa * segundos) - EPS * segundos


# Procura a fase com a maior demanda que ainda não foi atendida.
# Devolve -1 se toda a demanda já foi atendida.
def fase_com_maior_demanda(verdes, demandas):
    escolhida = -1
    maior_falta = 0
    for i in range(len(FASES)):
        if verdes[i] < FASES[i].maximo:
            falta = FASES[i].peso * max(0.0, demandas[i] - FASES[i].taxa * verdes[i])
            if falta > maior_falta:
                maior_falta = falta
                escolhida = i
    return escolhida


# Procura a fase que está mais abaixo do seu verde base.
def fase_mais_abaixo_da_base(verdes):
    escolhida = -1
    maior_diferenca = 0
    for i in range(len(FASES)):
        if verdes[i] < FASES[i].maximo:
            diferenca = FASES[i].base - verdes[i]
            if escolhida == -1 or diferenca > maior_diferenca:
                maior_diferenca = diferenca
                escolhida = i
    return escolhida


# A otimização não gasta segundos que não aumentam o benefício.
# Aqui esses segundos são entregues um a um para o ciclo fechar em 81 s.
def distribuir_sobra(verdes, demandas):
    resultado = list(verdes)
    sobra = VERDE_TOTAL - sum(resultado)
    for _ in range(sobra):
        escolhida = fase_com_maior_demanda(resultado, demandas)
        if escolhida == -1:
            escolhida = fase_mais_abaixo_da_base(resultado)
        resultado[escolhida] += 1
    return resultado


# Monta o dicionário que todos os algoritmos devolvem.
def montar_resposta(verdes, beneficio, demandas, trabalho):
    return {
        "verdes": distribuir_sobra(verdes, demandas),
        "verdes_dp": verdes,       # verdes antes de distribuir a sobra
        "beneficio": beneficio,
        "sobra": VERDE_TOTAL - sum(verdes),
        "trabalho": trabalho,      # quantas operações o método fez
    }


# Técnica 1: TABULAÇÃO (bottom-up). Complexidade O(n * T * K).
# dp[i][t] = melhor benefício das i primeiras fases usando no máximo t segundos.
def alocar_tabulacao(demandas):
    n = len(FASES)
    dp = []
    escolha = []
    for i in range(n + 1):
        dp.append([INVIAVEL] * (VERDE_TOTAL + 1))
        escolha.append([0] * (VERDE_TOTAL + 1))

    # Sem nenhuma fase, o benefício é zero
    for t in range(VERDE_TOTAL + 1):
        dp[0][t] = 0.0

    transicoes = 0
    for i in range(1, n + 1):
        fase = FASES[i - 1]
        for t in range(VERDE_TOTAL + 1):
            limite = min(fase.maximo, t)
            for s in range(fase.minimo, limite + 1):
                if dp[i - 1][t - s] == INVIAVEL:
                    continue
                transicoes += 1
                valor = dp[i - 1][t - s] + beneficio_fase(fase, demandas[i - 1], s)
                if valor > dp[i][t]:
                    dp[i][t] = valor
                    escolha[i][t] = s

    # Volta pela tabela para descobrir quanto cada fase recebeu
    verdes = [0] * n
    t = VERDE_TOTAL
    for i in range(n, 0, -1):
        verdes[i - 1] = escolha[i][t]
        t = t - verdes[i - 1]

    return montar_resposta(verdes, dp[n][VERDE_TOTAL], demandas, transicoes)


# Técnica 2: MEMOIZAÇÃO (top-down).
# É a mesma ideia da tabulação, mas escrita com recursão.
def alocar_memoizacao(demandas):

    # Devolve (melhor benefício das i primeiras fases, verde escolhido para a fase i)
    @lru_cache(maxsize=None)
    def melhor(i, t):
        if i == 0:
            return 0.0, 0

        fase = FASES[i - 1]
        melhor_valor = INVIAVEL
        melhor_s = 0
        limite = min(fase.maximo, t)
        for s in range(fase.minimo, limite + 1):
            anterior = melhor(i - 1, t - s)[0]
            if anterior == INVIAVEL:
                continue
            valor = anterior + beneficio_fase(fase, demandas[i - 1], s)
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_s = s
        return melhor_valor, melhor_s

    n = len(FASES)
    valor_otimo = melhor(n, VERDE_TOTAL)[0]

    verdes = [0] * n
    t = VERDE_TOTAL
    for i in range(n, 0, -1):
        verdes[i - 1] = melhor(i, t)[1]
        t = t - verdes[i - 1]

    subproblemas = melhor.cache_info().currsize
    return montar_resposta(verdes, valor_otimo, demandas, subproblemas)


# Força bruta: testa todas as combinações.
# Não decide o semáforo, serve só para conferir a DP e comparar o trabalho.
def alocar_forca_bruta(demandas):
    melhor_valor = INVIAVEL
    melhores_verdes = [0, 0, 0]
    combinacoes = 0

    for a in range(FASES[0].minimo, FASES[0].maximo + 1):
        for b in range(FASES[1].minimo, FASES[1].maximo + 1):
            for c in range(FASES[2].minimo, FASES[2].maximo + 1):
                if a + b + c > VERDE_TOTAL:
                    continue
                combinacoes += 1
                valor = (beneficio_fase(FASES[0], demandas[0], a)
                         + beneficio_fase(FASES[1], demandas[1], b)
                         + beneficio_fase(FASES[2], demandas[2], c))
                if valor > melhor_valor:
                    melhor_valor = valor
                    melhores_verdes = [a, b, c]

    return montar_resposta(melhores_verdes, melhor_valor, demandas, combinacoes)


# Arredonda as demandas para o múltiplo de 4 mais próximo.
# Assim situações parecidas viram a mesma e o cache é mais aproveitado.
def quantizar(demandas):
    estado = []
    for demanda in demandas:
        estado.append(int(demanda / 4 + 0.5) * 4)
    return tuple(estado)


# Técnica 3: guarda a resposta de cada estado de tráfego já calculado.
@lru_cache(maxsize=4096)
def alocar_cache(estado):
    return alocar_tabulacao(estado)

# simulador.py
# Faz o papel da câmera: sorteia quantos carros e pedestres chegam a cada segundo.
#
# Todas as constantes abaixo são premissas do grupo, não calibradas com dados reais.

import math
import random


HORIZONTE_S = 3600              # uma hora simulada
SEMENTE_PADRAO = 42

# Carros por segundo
TAXA_CARROS_PRINCIPAL = 0.22
TAXA_CARROS_TRANSVERSAL = 0.10

# Pedestres
TAXA_PEDESTRES_BASE = 0.03      # pedestres por segundo fora das rajadas
INTERVALO_TRENS_S = 300         # um trem a cada 5 minutos
PRIMEIRO_TREM_S = -180          # trem anterior ao início da hora (chega à rua aos 120 s)
PASSAGEIROS_POR_TREM = 250
FRACAO_NESTA_TRAVESSIA = 0.40
ATRASO_SAIDA_S = 300            # da plataforma até a rua: a estação é funda, cerca de 5 min
DECAIMENTO_S = 40               # quanto mais alto, mais devagar a rajada acaba
PROB_VULNERAVEL = 0.12


# Sorteia um valor com distribuição de Poisson (algoritmo de Knuth).
def amostrar_poisson(rng, taxa):
    if taxa <= 0:
        return 0
    limite = math.exp(-taxa)
    k = 0
    produto = 1.0
    while True:
        k += 1
        produto = produto * rng.random()
        if produto <= limite:
            return k - 1


def instantes_dos_trens():
    return list(range(PRIMEIRO_TREM_S, HORIZONTE_S, INTERVALO_TRENS_S))


# Taxa de pedestres em um segundo: a taxa base mais a rajada de cada trem.
def taxa_pedestres(segundo):
    pessoas_por_trem = PASSAGEIROS_POR_TREM * FRACAO_NESTA_TRAVESSIA
    taxa = TAXA_PEDESTRES_BASE
    for instante_trem in instantes_dos_trens():
        inicio = instante_trem + ATRASO_SAIDA_S
        if segundo >= inicio:
            decorrido = segundo - inicio
            taxa += (pessoas_por_trem / DECAIMENTO_S) * math.exp(-decorrido / DECAIMENTO_S)
    return taxa


# Gera uma hora de chegadas. A mesma semente gera sempre o mesmo cenário.
# Em "pedestres", cada segundo tem uma lista com True para quem é vulnerável.
def gerar_cenario(semente=SEMENTE_PADRAO):
    rng = random.Random(semente)
    carros_principal = []
    carros_transversal = []
    pedestres = []

    for segundo in range(HORIZONTE_S):
        carros_principal.append(amostrar_poisson(rng, TAXA_CARROS_PRINCIPAL))
        carros_transversal.append(amostrar_poisson(rng, TAXA_CARROS_TRANSVERSAL))

        quantidade = amostrar_poisson(rng, taxa_pedestres(segundo))
        pessoas = []
        for _ in range(quantidade):
            pessoas.append(rng.random() < PROB_VULNERAVEL)
        pedestres.append(pessoas)

    return {
        "carros_principal": carros_principal,
        "carros_transversal": carros_transversal,
        "pedestres": pedestres,
    }

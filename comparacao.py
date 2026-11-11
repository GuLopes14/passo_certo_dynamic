# comparacao.py
# Simula o mesmo cenário em 4 semáforos, segundo a segundo, usando filas.
#
# Decisões do modelo:
#   - O ciclo começa pelos pedestres, então o verde deles sempre abre no início.
#   - O "% a tempo" considera apenas quem começou a atravessar.

from collections import deque

from alocador import (
    CICLO,
    FASES,
    LARGURA_TRAVESSIA_M,
    PEDESTRES,
    PERDIDO,
    PRINCIPAL,
    TRANSVERSAL,
    VELOCIDADE_VULNERAVEL,
    alocar_cache,
    quantizar,
)
from simulador import HORIZONTE_S, gerar_cenario


FRACAO_CICLO_ANTERIOR = 0.5     # peso das chegadas do ciclo anterior na previsão
ORDEM_EXECUCAO = (PEDESTRES, PRINCIPAL, TRANSVERSAL)

# Verdes na ordem: via principal, pedestres, via transversal.
# Relato de quem atravessa: 12 s de verde + 7 s de vermelho piscante.
# Os 37 s e 28 s dos carros são supostos, pois o relato só fala do pedestre.
VERDES_ATUAL = (37, 12, 28)
LIMPEZA_ATUAL = 7

VERDES_PADRAO = (36, 17, 28)
VERDES_IGUALITARIO = (27, 27, 27)


# Quando "verdes" é None, o semáforo calcula o verde com a Programação Dinâmica.
def criar_semaforos():
    return [
        {"nome": "Atual (relatado)", "verdes": VERDES_ATUAL, "limpeza": LIMPEZA_ATUAL},
        {"nome": "Fixo padrão", "verdes": VERDES_PADRAO, "limpeza": PERDIDO},
        {"nome": "Fixo igualitário", "verdes": VERDES_IGUALITARIO, "limpeza": PERDIDO},
        {"nome": "Adaptativo (DP)", "verdes": None, "limpeza": PERDIDO},
    ]


# Coloca nas filas quem chegou no segundo t.
# Cada item da fila é (segundo de chegada, é vulnerável).
def registrar_chegadas(cenario, t, filas, chegadas_ciclo, total_chegadas):
    for _ in range(cenario["carros_principal"][t]):
        filas[PRINCIPAL].append((t, False))
    for _ in range(cenario["carros_transversal"][t]):
        filas[TRANSVERSAL].append((t, False))
    for vulneravel in cenario["pedestres"][t]:
        filas[PEDESTRES].append((t, vulneravel))

    quantidades = [
        cenario["carros_principal"][t],
        len(cenario["pedestres"][t]),
        cenario["carros_transversal"][t],
    ]
    for i in range(3):
        chegadas_ciclo[i] += quantidades[i]
        total_chegadas[i] += quantidades[i]


def media(valores):
    if len(valores) == 0:
        return 0.0
    return sum(valores) / len(valores)


# Simula uma hora de um semáforo e devolve as métricas.
def simular(cenario, semaforo, ordem=ORDEM_EXECUCAO):
    filas = [deque(), deque(), deque()]
    chegadas_ciclo = [0, 0, 0]
    total_chegadas = [0, 0, 0]
    atendidos = [0, 0, 0]
    esperas_carros = []
    esperas_pedestres = []
    vulneraveis_iniciaram = 0
    vulneraveis_a_tempo = 0
    pico_fila = 0
    verdes_pedestres = []
    t = 0

    while t < HORIZONTE_S:
        # A demanda é a fila atual mais 50% das chegadas do ciclo anterior
        demanda = []
        for i in range(3):
            demanda.append(len(filas[i]) + FRACAO_CICLO_ANTERIOR * chegadas_ciclo[i])

        if semaforo["verdes"] is None:
            verdes = alocar_cache(quantizar(demanda))["verdes"]
        else:
            verdes = semaforo["verdes"]

        assert sum(verdes) + semaforo["limpeza"] + PERDIDO + PERDIDO == CICLO, "O ciclo não fechou"
        verdes_pedestres.append(verdes[PEDESTRES])
        chegadas_ciclo = [0, 0, 0]
        inicio_ciclo = t

        for fase in ordem:
            verde = verdes[fase]
            if fase == PEDESTRES:
                limpeza = semaforo["limpeza"]
            else:
                limpeza = PERDIDO

            # O crédito acumula taxas quebradas (0,5/s atende 1 a cada 2 s)
            credito = 0.0

            for segundo in range(verde + limpeza):
                registrar_chegadas(cenario, t, filas, chegadas_ciclo, total_chegadas)

                if segundo < verde:
                    credito += FASES[fase].taxa
                    quantidade = int(credito)
                    credito -= quantidade

                    for _ in range(min(quantidade, len(filas[fase]))):
                        chegada, vulneravel = filas[fase].popleft()
                        espera = t - chegada
                        atendidos[fase] += 1

                        if fase != PEDESTRES:
                            esperas_carros.append(espera)
                        else:
                            esperas_pedestres.append(espera)
                            if vulneravel:
                                vulneraveis_iniciaram += 1
                                tempo_final = segundo + LARGURA_TRAVESSIA_M / VELOCIDADE_VULNERAVEL
                                if tempo_final <= verde + limpeza:
                                    vulneraveis_a_tempo += 1

                pico_fila = max(pico_fila, len(filas[PEDESTRES]))
                t += 1

        assert t - inicio_ciclo == CICLO, "O ciclo não durou 90 s"

    assert t == HORIZONTE_S, "A hora simulada não fechou"

    # Conservação: tudo que chegou foi atendido ou continua na fila
    for i in range(3):
        assert total_chegadas[i] == atendidos[i] + len(filas[i]), "Conservação violada"

    # Quem ficou na fila conta a espera até o fim da hora
    for fase in (PRINCIPAL, TRANSVERSAL):
        for chegada, _ in filas[fase]:
            esperas_carros.append(HORIZONTE_S - chegada)
    for chegada, _ in filas[PEDESTRES]:
        esperas_pedestres.append(HORIZONTE_S - chegada)

    porcentagem = 0.0
    if vulneraveis_iniciaram > 0:
        porcentagem = 100.0 * vulneraveis_a_tempo / vulneraveis_iniciaram

    return {
        "espera_carros": media(esperas_carros),
        "espera_pedestres": media(esperas_pedestres),
        "pct_no_verde_vulneraveis": porcentagem,
        "pico_fila_pedestres": pico_fila,
        "verde_min_pedestres": min(verdes_pedestres),
        "verde_max_pedestres": max(verdes_pedestres),
    }


# Roda todos os semáforos em várias sementes e devolve a média de cada métrica.
def repetir(sementes, ordem=ORDEM_EXECUCAO):
    semaforos = criar_semaforos()
    valores = {}
    for semaforo in semaforos:
        valores[semaforo["nome"]] = {}

    for semente in sementes:
        cenario = gerar_cenario(semente)
        for semaforo in semaforos:
            resultado = simular(cenario, semaforo, ordem)
            for metrica in resultado:
                if metrica not in valores[semaforo["nome"]]:
                    valores[semaforo["nome"]][metrica] = []
                valores[semaforo["nome"]][metrica].append(resultado[metrica])

    medias = {}
    for nome in valores:
        medias[nome] = {}
        for metrica in valores[nome]:
            medias[nome][metrica] = media(valores[nome][metrica])
    return medias

# interativo.py
# Demonstração: "a câmera detectou X pessoas e Y carros, portanto o tempo será Z".
#
# A câmera não existe no protótipo, então o usuário digita o que ela teria contado.

import time

from alocador import (
    FASES,
    LARGURA_TRAVESSIA_M,
    PEDESTRES,
    PERDIDO,
    PRINCIPAL,
    TRANSVERSAL,
    VELOCIDADE_VULNERAVEL,
    alocar_cache,
    alocar_forca_bruta,
    alocar_memoizacao,
    alocar_tabulacao,
)
from comparacao import (
    LIMPEZA_ATUAL,
    ORDEM_EXECUCAO,
    VERDES_ATUAL,
    VERDES_IGUALITARIO,
    VERDES_PADRAO,
)


LARGURA_TELA = 78


# Quantas pessoas ou carros cabem em um verde
def capacidade(fase, verde):
    return int(fase.taxa * verde)


# Até quantos segundos depois de abrir um pedestre vulnerável termina a tempo
def limite_inicio_vulneravel(verde, limpeza):
    return verde + limpeza - LARGURA_TRAVESSIA_M / VELOCIDADE_VULNERAVEL


# Explica por que a fase recebeu aquele tempo de verde
def explicar_fase(fase, demanda, verde_dp, verde_final):
    falta_atender = demanda > capacidade(fase, verde_final)

    if falta_atender and verde_final == fase.maximo:
        texto = f"a demanda passa do que cabe no máximo de {fase.maximo} s"
    elif falta_atender and verde_final == fase.minimo:
        texto = f"ficou no mínimo de {fase.minimo} s, pois as outras fases rendem mais benefício por segundo"
    elif falta_atender:
        texto = "recebeu o tempo que restou depois das fases de maior benefício"
    elif verde_dp == fase.minimo:
        texto = f"o mínimo de {fase.minimo} s já atende a demanda"
    else:
        texto = "recebeu o necessário para atender toda a demanda"

    extra = verde_final - verde_dp
    if extra > 0:
        texto += f"; ganhou mais {extra} s da sobra do ciclo"
    return texto


# Executa o método várias vezes e devolve o tempo médio em milissegundos
def medir_tempo(metodo, demandas, repeticoes):
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        metodo(demandas)
    return (time.perf_counter() - inicio) / repeticoes * 1000


def formatar_ms(valor):
    if valor < 0.01:
        return "menos de 0,01 ms"
    return f"{valor:.2f}".replace(".", ",") + " ms"


def mostrar_detectado(demandas):
    print()
    print("=" * LARGURA_TELA)
    print("O QUE A CÂMERA DETECTOU (valores informados por você)")
    print("=" * LARGURA_TELA)
    for i in ORDEM_EXECUCAO:
        print(f"  {FASES[i].nome:<26}{demandas[i]:>6}")


def mostrar_verdes(demandas, resposta):
    print()
    print("PORTANTO, O VERDE DESTE CICLO SERÁ")
    print("-" * LARGURA_TELA)
    print(f"{'Fase':<26}{'Detectados':>12}{'Verde':>10}{'Atendidos':>12}{'Ficam':>8}")

    for i in ORDEM_EXECUCAO:
        fase = FASES[i]
        verde = resposta["verdes"][i]
        atendidos = min(demandas[i], capacidade(fase, verde))
        ficam = demandas[i] - atendidos
        texto_verde = str(verde) + " s"
        print(f"{fase.nome:<26}{demandas[i]:>12}{texto_verde:>10}{atendidos:>12}{ficam:>8}")
    print("\"Ficam\" são os que continuam esperando o próximo ciclo.")

    print()
    print("POR QUÊ")
    for i in ORDEM_EXECUCAO:
        motivo = explicar_fase(FASES[i], demandas[i], resposta["verdes_dp"][i], resposta["verdes"][i])
        print(f"  - {FASES[i].nome}: {motivo}.")


def mostrar_linha_atendidos(nome, verdes, demandas):
    pedestres = min(demandas[PEDESTRES], capacidade(FASES[PEDESTRES], verdes[PEDESTRES]))
    principal = min(demandas[PRINCIPAL], capacidade(FASES[PRINCIPAL], verdes[PRINCIPAL]))
    transversal = min(demandas[TRANSVERSAL], capacidade(FASES[TRANSVERSAL], verdes[TRANSVERSAL]))
    carros = principal + transversal
    total = pedestres + carros
    texto_verdes = f"{verdes[PEDESTRES]}/{verdes[PRINCIPAL]}/{verdes[TRANSVERSAL]}"
    print(f"{nome:<20}{texto_verdes:<27}{pedestres:>10}{carros:>8}{total:>8}")


def mostrar_atendidos(demandas, resposta):
    print()
    print("QUANTOS FORAM ATENDIDOS NESTE CICLO")
    print("-" * LARGURA_TELA)
    print(f"{'Divisão':<20}{'Verdes (Ped/Princ/Transv)':<27}{'Pedestres':>10}{'Carros':>8}{'Total':>8}")
    mostrar_linha_atendidos("Passo Certo (DP)", resposta["verdes"], demandas)
    mostrar_linha_atendidos("Fixo igualitário", VERDES_IGUALITARIO, demandas)
    mostrar_linha_atendidos("Fixo padrão", VERDES_PADRAO, demandas)
    mostrar_linha_atendidos("Atual (relatado)", VERDES_ATUAL, demandas)
    print("Os 37 s e 28 s dos carros no \"Atual\" são supostos; o relato só cobre o pedestre.")


def mostrar_travessia(resposta):
    verde_novo = resposta["verdes"][PEDESTRES]
    verde_atual = VERDES_ATUAL[PEDESTRES]
    texto_atual = f"{verde_atual} s + {LIMPEZA_ATUAL} s piscante"
    texto_novo = f"{verde_novo} s + {PERDIDO} s"

    limite_atual = limite_inicio_vulneravel(verde_atual, LIMPEZA_ATUAL)
    limite_novo = limite_inicio_vulneravel(verde_novo, PERDIDO)
    texto_limite_atual = f"{limite_atual:.1f}".replace(".", ",") + " s"
    texto_limite_novo = f"{limite_novo:.1f}".replace(".", ",") + " s"

    print()
    print(f"{'Neste ciclo':<34}{'Atual (relatado)':>20}{'Passo Certo':>16}")
    print("-" * 70)
    print(f"{'Verde de pedestres':<34}{texto_atual:>20}{texto_novo:>16}")
    print(f"{'Vulnerável termina se começar até':<34}{texto_limite_atual:>20}{texto_limite_novo:>16}")


def mostrar_trabalho(demandas, tabulacao, memoizacao, forca_bruta):
    # Chama uma vez para garantir que a leitura já está guardada no cache
    alocar_cache(demandas)

    tempo_forca_bruta = medir_tempo(alocar_forca_bruta, demandas, 5)
    tempo_tabulacao = medir_tempo(alocar_tabulacao, demandas, 20)
    tempo_memoizacao = medir_tempo(alocar_memoizacao, demandas, 20)
    tempo_cache = medir_tempo(alocar_cache, demandas, 1000)

    combinacoes = f"{forca_bruta['trabalho']:,}".replace(",", ".") + " combinações"
    transicoes = f"{tabulacao['trabalho']:,}".replace(",", ".") + " transições"
    subproblemas = f"{memoizacao['trabalho']:,}".replace(",", ".") + " subproblemas"

    print()
    print("QUANTO TRABALHO FOI PRECISO PARA ACHAR A MELHOR DIVISÃO")
    print("-" * LARGURA_TELA)
    print(f"{'Força bruta (testa tudo)':<30}{combinacoes:<26}{formatar_ms(tempo_forca_bruta):>20}")
    print(f"{'Tabulação':<30}{transicoes:<26}{formatar_ms(tempo_tabulacao):>20}")
    print(f"{'Memoização':<30}{subproblemas:<26}{formatar_ms(tempo_memoizacao):>20}")
    print(f"{'Mesma leitura, já no cache':<30}{'resposta guardada':<26}{formatar_ms(tempo_cache):>20}")
    print()

    # Os três métodos precisam chegar ao mesmo benefício
    diferenca_memo = abs(tabulacao["beneficio"] - memoizacao["beneficio"])
    diferenca_bruta = abs(tabulacao["beneficio"] - forca_bruta["beneficio"])
    if diferenca_memo < 1e-9 and diferenca_bruta < 1e-9:
        print("A força bruta confirmou: a DP encontrou a melhor divisão possível.")
    else:
        print("ATENÇÃO: os métodos chegaram a resultados diferentes.")
    print("=" * LARGURA_TELA)


# Calcula o verde para o que a câmera detectou e mostra tudo na tela.
# Aqui a demanda é exatamente o valor digitado, sem quantizar.
def mostrar_decisao(pessoas, carros_principal, carros_transversal):
    demandas = (carros_principal, pessoas, carros_transversal)
    tabulacao = alocar_tabulacao(demandas)
    memoizacao = alocar_memoizacao(demandas)
    forca_bruta = alocar_forca_bruta(demandas)

    mostrar_detectado(demandas)
    mostrar_verdes(demandas, tabulacao)
    mostrar_atendidos(demandas, tabulacao)
    mostrar_travessia(tabulacao)
    mostrar_trabalho(demandas, tabulacao, memoizacao, forca_bruta)


# Pede um número inteiro. Devolve None se o usuário quiser sair.
def ler_inteiro(rotulo):
    while True:
        try:
            texto = input(rotulo + ": ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None

        if texto == "s" or texto == "sair":
            return None

        try:
            valor = int(texto)
        except ValueError:
            print("Digite um número inteiro, por exemplo 25, ou 's' para sair.")
            continue

        if valor < 0:
            print("A contagem não pode ser negativa.")
            continue
        return valor


def sessao_camera():
    print()
    print("Informe o que a câmera teria detectado. Digite 's' para voltar.")
    while True:
        pessoas = ler_inteiro("Pessoas detectadas na calçada")
        if pessoas is None:
            return
        carros_principal = ler_inteiro("Carros detectados na via principal")
        if carros_principal is None:
            return
        carros_transversal = ler_inteiro("Carros detectados na via transversal")
        if carros_transversal is None:
            return

        mostrar_decisao(pessoas, carros_principal, carros_transversal)
        print("Próxima leitura ('s' para voltar).")

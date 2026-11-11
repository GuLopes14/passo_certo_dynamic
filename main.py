# main.py
# Programa principal do projeto Passo Certo.
#
# Para executar:
#   python main.py               abre o menu
#   python main.py --relatorio   mostra direto o resultado da simulação

import sys

from alocador import PEDESTRES, PRINCIPAL, TRANSVERSAL
from comparacao import repetir
from interativo import sessao_camera
from simulador import INTERVALO_TRENS_S


SEMENTES = range(1, 31)     # 30 cenários
ORDEM_ALTERNATIVA = (PRINCIPAL, PEDESTRES, TRANSVERSAL)

ATUAL = "Atual (relatado)"
PADRAO = "Fixo padrão"
IGUALITARIO = "Fixo igualitário"
DP = "Adaptativo (DP)"


def formatar_tempo(segundos):
    total = int(segundos + 0.5)
    if total < 60:
        return f"{total} s"
    return f"{total // 60} min {total % 60} s"


def imprimir_titulo(texto):
    print()
    print("=" * 94)
    print(texto)
    print("=" * 94)


def imprimir_linha_semaforo(rotulo, dados):
    espera_pedestres = formatar_tempo(dados["espera_pedestres"])
    espera_carros = formatar_tempo(dados["espera_carros"])
    vulneraveis = f"{dados['pct_no_verde_vulneraveis']:.0f}%"
    pico = f"{dados['pico_fila_pedestres']:.0f}"
    print(f"{rotulo:<22}{espera_pedestres:>18}{espera_carros:>16}{vulneraveis:>23}{pico:>15}")


def imprimir_tabela(resumo):
    print(f"{'Semáforo':<22}{'Espera pedestres':>18}{'Espera carros':>16}{'Vulneráveis a tempo*':>23}{'Pico da fila':>15}")
    print("-" * 94)
    imprimir_linha_semaforo(ATUAL, resumo[ATUAL])
    imprimir_linha_semaforo(PADRAO, resumo[PADRAO])
    imprimir_linha_semaforo(IGUALITARIO, resumo[IGUALITARIO])
    imprimir_linha_semaforo("Passo Certo (DP)", resumo[DP])
    print("* Pedestres vulneráveis que terminam a travessia a tempo, entre os que começaram.")


def imprimir_conclusoes(resumo):
    espera_dp = formatar_tempo(resumo[DP]["espera_pedestres"])
    espera_padrao = formatar_tempo(resumo[PADRAO]["espera_pedestres"])
    espera_igualitario = formatar_tempo(resumo[IGUALITARIO]["espera_pedestres"])
    vulneraveis_dp = f"{resumo[DP]['pct_no_verde_vulneraveis']:.0f}%"
    vulneraveis_atual = f"{resumo[ATUAL]['pct_no_verde_vulneraveis']:.0f}%"
    carros_dp = formatar_tempo(resumo[DP]["espera_carros"])
    custo_carros = formatar_tempo(resumo[DP]["espera_carros"] - resumo[PADRAO]["espera_carros"])
    verde_min = f"{resumo[DP]['verde_min_pedestres']:.0f}"
    verde_max = f"{resumo[DP]['verde_max_pedestres']:.0f}"
    pico_dp = f"{resumo[DP]['pico_fila_pedestres']:.0f}"
    pico_igualitario = f"{resumo[IGUALITARIO]['pico_fila_pedestres']:.0f}"

    print()
    print("O QUE ISSO MOSTRA")
    print(f"  - Pedestres: espera média de {espera_dp} com o Passo Certo, contra {espera_padrao}")
    print(f"    no Fixo padrão e {espera_igualitario} no Fixo igualitário.")
    print(f"  - Vulneráveis: {vulneraveis_dp} terminam a tempo com o Passo Certo, contra {vulneraveis_atual} no semáforo atual.")
    print(f"  - Custo: os carros esperam {carros_dp} em média, {custo_carros} a mais que no Fixo padrão.")
    print(f"  - Como: o verde de pedestres varia de {verde_min} s a {verde_max} s e só cresce quando há multidão.")
    print(f"  - Limite: o pico da fila chega a {pico_dp} pessoas no Passo Certo ({pico_igualitario} no Fixo igualitário),")
    print("    pois o algoritmo só reage depois que a rajada de pessoas aparece.")


def imprimir_linha_ordem(rotulo, dados):
    espera_pedestres = formatar_tempo(dados[DP]["espera_pedestres"])
    espera_carros = formatar_tempo(dados[DP]["espera_carros"])
    custo = formatar_tempo(dados[DP]["espera_carros"] - dados[PADRAO]["espera_carros"])
    print(f"{rotulo:<28}{espera_pedestres:>18}{espera_carros:>16}{custo:>32}")


# Mostra o quanto o resultado muda se o ciclo começar pela via principal
def imprimir_ordem_das_fases(resumo, resumo_alternativo):
    print()
    print("E SE A ORDEM DAS FASES MUDAR? (Passo Certo)")
    print(f"{'O ciclo começa por':<28}{'Espera pedestres':>18}{'Espera carros':>16}{'Carros a mais que Fixo padrão':>32}")
    print("-" * 94)
    imprimir_linha_ordem("Pedestres (usada na tabela)", resumo)
    imprimir_linha_ordem("Via principal", resumo_alternativo)
    print("Começar pelos pedestres favorece o Passo Certo: eles são atendidos logo depois da leitura da fila.")


def imprimir_resultado():
    resumo = repetir(SEMENTES)
    resumo_alternativo = repetir(SEMENTES, ORDEM_ALTERNATIVA)

    imprimir_titulo("RESULTADO DA SIMULAÇÃO")
    print(f"Uma hora de movimento, com saída de trem a cada {INTERVALO_TRENS_S // 60} min. Média de {len(SEMENTES)} cenários.")
    print()
    imprimir_tabela(resumo)
    imprimir_conclusoes(resumo)
    imprimir_ordem_das_fases(resumo, resumo_alternativo)

    print()
    print("ATENÇÃO: o movimento é simulado e não foi calibrado com dados reais. Os números")
    print("comparam os semáforos entre si e não preveem o cruzamento real. No \"Atual\",")
    print("a espera é alta porque, neste modelo, a fila cresce durante a hora inteira.")


def menu():
    print("PASSO CERTO - Av. Paulista x Rua Augusta (saída da estação Consolação)")
    while True:
        print()
        print("1 - Informar o que a câmera detectou e ver o tempo do semáforo")
        print("2 - Ver o resultado da simulação")
        print("0 - Sair")
        try:
            opcao = input("Escolha: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if opcao == "1":
            sessao_camera()
        elif opcao == "2":
            imprimir_resultado()
        elif opcao == "0" or opcao == "s" or opcao == "sair":
            return
        else:
            print("Opção inválida. Digite 1, 2 ou 0.")


if __name__ == "__main__":
    if "--relatorio" in sys.argv:
        imprimir_resultado()
    else:
        menu()

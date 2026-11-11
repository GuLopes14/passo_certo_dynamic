# Passo Certo

Divisão do tempo de verde de um semáforo com Programação Dinâmica, pensada para quem atravessa a pé.

## Integrantes

| RM | Nome |
|---|---|
| 571341 | Felipe Horta Gresele |
| 570887 | Gustavo Lopes Santos da Silva |
| 571721 | Lucas Nicolini Martins de Souza |
| 570800 | Renato de Freitas David Campiteli |
| 573253 | Tiago Augusto Desiderato Ferro |

## Ficha da CitizenTech

| Campo | Descrição |
|---|---|
| Nome | Passo Certo |
| Território | Cruzamento da Av. Paulista com a Rua Augusta, saída da estação Consolação do Metrô (lado do Conjunto Nacional), São Paulo |
| Cidadão principal | Pedestre vulnerável (idoso, pessoa com deficiência, pessoa com carrinho de bebê) que sai da estação |
| Cidadão secundário | Motorista que passa pelo cruzamento |
| Problema | Hipótese avaliada por simulação: quando um trem desembarca, muita gente chega de uma vez à travessia, e o verde de pedestres pode não dar conta dessa multidão no pico |
| Proposta | Uma câmera contaria pedestres e carros, e um algoritmo de Programação Dinâmica dividiria o verde do ciclo entre as fases |
| Protótipo | A câmera **não** foi implementada. Uma simulação com dados sintéticos faz o papel dela |

## Escuta do território

O ponto de partida é o relato de quem atravessa o cruzamento: o sinal de pedestres fica **12 s em verde** e depois **7 s em vermelho piscante**, em uma travessia de **12,3 m** de largura.

> "Eu trabalho no conjunto nacional e todos os dias pego o metrô da consolação, portanto sempre passo por este cruzamento, acredito que o tempo que fico esperando é cerca de 20 ou 19 segundos, levando em conta que o semáforo fica aberto uns 14 segundos e o piscante fica uns 5 segundos."
>
> Doutora de uma clínica odontológica chamda LLanos, localizada no conjunto nacional.

O relato cobre apenas o tempo do pedestre. O tipo de controle do semáforo atual não foi confirmado.

## A conta simples

Para um pedestre vulnerável, a 0,9 m/s:

- Atravessar 12,3 m leva 13,67 s.
- Arredondando para 14 s e somando 3 s de reação, são necessários **17 s**.
- O relato indica **19 s** disponíveis (12 s + 7 s), uma **folga de 2 s**.
- Para terminar a tempo, a pessoa precisa começar nos primeiros **5 s** do verde (mais exatamente, até 5,33 s).

Portanto, 19 s cobrem quem começa logo. **O problema estudado aqui é a capacidade no pico**: a quantidade de pessoas que consegue iniciar a travessia em cada ciclo quando a estação despeja uma multidão.

## Como executar

É preciso ter Python 3.9 ou mais recente. O projeto usa apenas a biblioteca padrão, sem `pip install`.

Abre o menu interativo:

```bash
python main.py
```

Imprime direto o resultado da simulação (o mesmo da opção 2 do menu):

```bash
python main.py --relatorio
```

## Demonstração interativa

A demonstração responde à pergunta central do projeto: **"a câmera detectou X pessoas e Y carros; quanto tempo o semáforo vai dar a cada fase?"**. A câmera não existe no protótipo, então quem usa o programa digita a contagem que ela teria feito, e o verde é decidido pelo mesmo algoritmo de Programação Dinâmica da simulação.

Na opção 1 do menu, com 120 pessoas, 20 carros na via principal e 9 na transversal:

```text
PORTANTO, O VERDE DESTE CICLO SERÁ
------------------------------------------------------------------------------
Fase                        Detectados     Verde   Atendidos   Ficam
Pedestres                          120      45 s          90      30
Carros via principal                20      20 s          20       0
Carros via transversal               9      16 s           8       1
"Ficam" são os que continuam esperando o próximo ciclo.

POR QUÊ
  - Pedestres: a demanda passa do que cabe no máximo de 45 s.
  - Carros via principal: recebeu o necessário para atender toda a demanda.
  - Carros via transversal: recebeu o tempo que restou depois das fases de maior benefício.

QUANTOS FORAM ATENDIDOS NESTE CICLO
------------------------------------------------------------------------------
Divisão             Verdes (Ped/Princ/Transv)   Pedestres  Carros   Total
Passo Certo (DP)    45/20/16                           90      28     118
Fixo igualitário    27/27/27                           54      29      83
Fixo padrão         17/36/28                           34      29      63
Atual (relatado)    12/37/28                           24      29      53
Os 37 s e 28 s dos carros no "Atual" são supostos; o relato só cobre o pedestre.

Neste ciclo                           Atual (relatado)     Passo Certo
----------------------------------------------------------------------
Verde de pedestres                 12 s + 7 s piscante      45 s + 3 s
Vulnerável termina se começar até                5,3 s          34,3 s

QUANTO TRABALHO FOI PRECISO PARA ACHAR A MELHOR DIVISÃO
------------------------------------------------------------------------------
Força bruta (testa tudo)      15.399 combinações                     6,65 ms
Tabulação                     4.621 transições                       0,97 ms
Memoização                    152 subproblemas                       0,45 ms
Mesma leitura, já no cache    resposta guardada             menos de 0,01 ms

A força bruta confirmou: a DP encontrou a melhor divisão possível.
```

As contagens de trabalho não dependem da leitura, e os tempos são medidos a cada execução, então variam de um computador para outro. Com apenas 3 fases, a força bruta ainda é rápida: a economia da Programação Dinâmica cresce com o número de fases, porque as combinações se multiplicam a cada fase nova.

Com a calçada e as vias vazias (0, 0 e 0), o semáforo volta ao padrão de 17 s para pedestres, 36 s para a via principal e 28 s para a transversal.

Cada leitura representa **um único ciclo**: o programa usa exatamente os valores digitados e não leva quem ficou esperando para a leitura seguinte. Já a simulação da hora, usada no relatório, estima a demanda (fila atual mais 50% das chegadas do ciclo anterior) e quantiza o estado.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Menu do programa e resultado da simulação |
| `interativo.py` | Demonstração "a câmera detectou X e Y, portanto o tempo será Z" |
| `alocador.py` | Núcleo de Programação Dinâmica |
| `simulador.py` | Geração das chegadas, com seed fixa |
| `comparacao.py` | Simulação dos 4 semáforos e métricas |
| `README.md` | Este documento |

## Os três algoritmos

O ciclo tem 90 s e cada uma das 3 fases perde 3 s, o que deixa **81 s de verde** para dividir. O problema é uma **mochila de grupos**: as fases são os grupos de itens, os segundos de verde são a capacidade e os segundos dados a cada fase são a escolha.

O benefício de uma fase é `peso * min(demanda, taxa * segundos) - EPS * segundos`, com `EPS = 1e-3`, para evitar verde à toa.

| Fase | Taxa (por s) | Mínimo | Máximo | Peso | Base |
|---|---|---|---|---|---|
| Carros via principal | 1,0 | 10 | 60 | 1,0 | 36 |
| Pedestres | 2,0 | 17 | 45 | 2,0 | 17 |
| Carros via transversal | 0,5 | 10 | 60 | 1,0 | 28 |

1. **Tabulação (`alocar_tabulacao`).** Abordagem bottom-up. `dp[i][t]` é o melhor benefício das `i` primeiras fases com no máximo `t` segundos, e uma tabela de escolhas permite reconstruir a resposta. A complexidade é O(n·T·K), com `n` fases, capacidade `T` e `K` opções por fase.
2. **Memoização (`alocar_memoizacao`).** Abordagem top-down com a mesma recorrência, escrita como recursão com `lru_cache` sobre `(fase, tempo)`. Chega ao mesmo benefício da tabulação, o que é conferido a cada leitura no modo interativo.
3. **Cache de estados (`quantizar` + `alocar_cache`).** As demandas são arredondadas para múltiplos de 4 e a resposta de cada estado de tráfego fica guardada em um `lru_cache`, o que evita recalcular situações já vistas durante a simulação.

Uma força bruta (`alocar_forca_bruta`) testa todas as combinações válidas. Ela não decide o semáforo: serve para confirmar que a Programação Dinâmica encontrou o ótimo e para medir o trabalho economizado.

A otimização não gasta verde que não aumenta o benefício. Os segundos que sobram são entregues um a um, respeitando o máximo, à fase com maior demanda ponderada ainda não atendida. Se toda a demanda foi atendida, vão para a fase mais abaixo de seu verde base. Assim o ciclo sempre fecha em 81 s de verde e, sem tráfego especial, volta ao padrão 36/17/28.

## Funcionalidades

- Modo interativo: informa-se a contagem da câmera e o programa mostra o verde de cada fase, o motivo, quantos cada divisão do verde atenderia e o trabalho de cada método para achar a melhor divisão.
- Divisão ótima do verde por tabulação ou memoização.
- Verde mínimo de pedestres calculado a partir da largura da travessia e da velocidade do pedestre vulnerável.
- Geração reproduzível de uma hora de chegadas, com rajadas após cada trem.
- Comparação de 4 semáforos no mesmo cenário, com filas FIFO, segundo a segundo.
- Repetição em 30 cenários, com a média dos resultados.
- Verificações internas de conservação (tudo que chegou foi atendido ou continua na fila) e de fechamento do ciclo em 90 s.

## Os 4 semáforos comparados

| Semáforo | Verdes (principal / pedestres / transversal) | Observação |
|---|---|---|
| Atual (relatado) | 37 / 12 / 28, mais 7 s de piscante para pedestres | Os 12 s + 7 s vêm do relato. Os 37 s e 28 s dos carros são **supostos**, pois o relato só informa o pedestre, e foram escolhidos para o ciclo fechar em 90 s |
| Fixo padrão | 36 / 17 / 28 | Plano constante, com o pedestre no mínimo calculado |
| Fixo igualitário | 27 / 27 / 27 | Divide o verde em partes iguais |
| Adaptativo (DP) | Calculado a cada ciclo | Usa como demanda a fila atual mais 50% das chegadas do ciclo anterior, quantiza e chama `alocar_cache` |

O "Atual" é simulado com tempos constantes apenas porque o relato traz um único valor, o que não diz nada sobre como o semáforo real é controlado.

Na fase de pedestres, um pedestre vulnerável atendido no segundo `e` do verde termina a tempo se `e + largura / velocidade <= verde + limpeza`, com velocidade de 0,9 m/s. A limpeza é o vermelho piscante: 7 s no "Atual" e 3 s (o tempo perdido) nos outros semáforos.

## Resultados (média de 30 cenários, seeds 1 a 30)

Valores copiados da saída de `python main.py --relatorio`, que é o mesmo resultado da opção 2 do menu.

| Semáforo | Espera pedestres | Espera carros | Vulneráveis a tempo | Pico da fila (pessoas) |
|---|---|---|---|---|
| Atual (relatado) | 9 min 46 s | 23 s | 49% | 418 |
| Fixo padrão | 2 min 3 s | 24 s | 42% | 99 |
| Fixo igualitário | 51 s | 30 s | 69% | 91 |
| Passo Certo (DP) | 42 s | 32 s | 79% | 91 |

"Vulneráveis a tempo" são os pedestres vulneráveis que terminam a travessia a tempo, entre os que começaram a atravessar. Quem ficou na fila ao fim da hora não entra nesse percentual, mas conta na espera, medida até o fim da hora.

### Leitura honesta

- **Os números vêm de dados simulados e não calibrados.** Eles servem para comparar estratégias no mesmo cenário, não para prever o cruzamento real.
- **O "Atual" está saturado.** Neste modelo, a fila cresce a hora inteira. Os valores absolutos dessa linha, como a espera de 9 min 46 s, não são previsão.
- **O ganho vem de estender o verde de pedestres no pico, até 45 s, e não do mínimo de 17 s.** O "Fixo padrão" já usa 17 s e tem espera média de 2 min 3 s, contra 42 s do Passo Certo.
- **Os carros pagam a conta.** A espera deles é a maior entre os semáforos: 32 s no Passo Certo, 8 s a mais que no "Fixo padrão".
- **O "Fixo igualitário" é um concorrente forte e mais simples.** Ele fica em 51 s de espera de pedestres e 30 s de carros, sem nenhuma câmera. O Passo Certo fica à frente na espera de pedestres (42 s) e nos vulneráveis que terminam a tempo (79% contra 69%), com carros em 32 s.
- **A vantagem depende de picos fortes.** Com trens mais frequentes e o mesmo volume de pessoas, as rajadas diminuem e a vantagem sobre o "Fixo igualitário" tende a encolher.
- **Os números são sensíveis ao momento em que a multidão chega.** Pequenas mudanças nesse instante alteram em que parte do ciclo ela encontra o semáforo.
- **Mais verde mínimo não melhora, sozinho, a travessia a tempo.** O "Atual" (49%) supera o "Fixo padrão" (42%), porque seus 7 s de piscante protegem melhor quem inicia a travessia nos últimos segundos. O indicador melhora no Passo Certo (79%), mas continua abaixo de 100%: quem começa no fim de um verde longo pode não terminar a tempo.
- **O Passo Certo não reduz o pico da fila em relação ao "Fixo igualitário"** (91 pessoas nos dois). Ele reage depois que a rajada aparece, e o ciclo em que ela começa ainda foi planejado sem ela.

### Ordem das fases

Os resultados acima usam a ordem pedestres, via principal, via transversal, escolha do modelo para que apenas a duração do verde varie entre os semáforos. Essa ordem favorece o Passo Certo, pois os pedestres são atendidos logo depois da leitura da fila. Com o ciclo começando pela via principal, o resultado do Passo Certo muda assim:

| O ciclo começa por | Espera pedestres | Espera carros | Carros a mais que Fixo padrão |
|---|---|---|---|
| Pedestres (usada na tabela) | 42 s | 32 s | 8 s |
| Via principal | 55 s | 30 s | 6 s |

## Premissas e limitações

Todas as premissas a seguir são constantes nomeadas e comentadas no código, e **não foram calibradas com dados reais**.

- Carros: 0,22 por segundo na via principal e 0,10 por segundo na transversal.
- Pedestres: 0,03 por segundo, mais rajadas após cada trem.
- Trens a cada 5 min, com 250 passageiros, dos quais 40% usam esta travessia. O intervalo real da Linha 2-Verde não foi confirmado em fonte oficial.
- Da plataforma até a rua são cerca de 5 min, porque a estação é funda. A primeira multidão chega à rua aos 120 s da simulação, e cada chegada decai exponencialmente com constante de 40 s.
- Cada pedestre é vulnerável com probabilidade de 12%.
- Velocidade de 0,9 m/s para o pedestre vulnerável e atendimento de 2 pedestres por segundo.
- Os pesos, os limites de verde e os tempos dos carros no "Atual" são escolhas do modelo.

Limitações:

- A câmera não existe no protótipo. No modo interativo as contagens são digitadas, e na simulação elas são perfeitas, sem erro de detecção.
- O cruzamento é tratado isoladamente, sem coordenação com os semáforos vizinhos da Av. Paulista.
- A simulação cobre uma hora e não considera outros horários, chuva ou eventos.
- Uma caminhada longa tende a espalhar o grupo até a rua, o que suavizaria as rajadas. O modelo não representa esse efeito além da constante de 40 s.
- O modelo não representa conversões, ônibus, ciclistas nem pedestres que atravessam fora do verde.
- O peso 2,0 dado aos pedestres é uma escolha de valor. Pesos diferentes mudam a divisão do verde.

## Referências

- BELLMAN, R. *Dynamic Programming*. Princeton University Press, 1957.
- CORMEN, T. H. et al. *Introduction to Algorithms*. MIT Press.
- KNUTH, D. E. *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*. Addison-Wesley.
- CONTRAN. *Manual Brasileiro de Sinalização de Trânsito, Volume V: Sinalização Semafórica*.
- Documentação do Python: [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache), [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) e [`random`](https://docs.python.org/3/library/random.html).

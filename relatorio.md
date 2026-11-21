# Relatório — Parte 1: Labirinto com Chaves (Grafo de Estados)

Teoria dos Grafos — 2026.2

**Integrantes:**

- Amanda Luz
- Eric Albuquerque
- Mircio Ferreira
- Gabriel Aniceto
- Caio Almeida

**Orientadora:**

- Laura Alvez

---

## 1. Introdução

<!-- Problema, objetivo e visão geral do projeto. -->

- Descrição do problema: O jogador começa na casa `S` de um labirinto e precisa chegar à saída `G` pelo caminho de menor custo. O mapa tem paredes, que não podem ser atravessadas, e terrenos com custos diferentes. Há chaves, que o jogador pega ao entrar na casa e guarda para sempre, e portas, que só podem ser atravessadas por quem já tem a chave correspondente. Há também esteiras de mão única e casas de bônus. Como a mesma casa pode ser visitada com conjuntos de chaves diferentes, o mapa não pode ser tratado como o grafo: o problema é modelado como um grafo de estados, em que cada estado combina a posição, as chaves coletadas e os bônus já consumidos.
- Mapas utilizados: Os mapas `m01` a `m08` foram fornecidos pela orientadora como um desafio a ser debatido pelo grupo. Cada um exercita uma situação diferente: custos de terreno, uma ou três chaves, esteiras, bônus, fonte de energia, um mapa sem solução e um mapa grande. Além deles, o grupo criou mapas próprios a partir de um gerador de mapas. `m09` a `m11`
- Tabela de custos por terreno: A orientadora também indicou a tabela de custos abaixo, que não foi escolhida pelo grupo. O custo de um movimento é o custo da casa de destino.

| Símbolo | Terreno | Custo de entrar |
|---|---|---|
| `.` | Chão | 1 |
| `S` / `G` | Início / saída | 1 |
| `,` | Lama | 3 |
| `~` | Água | 5 |
| `a`–`d` | Chave | 1 |
| `A`–`D` | Porta (exige a chave correspondente) | 1 |
| `>` `<` `^` `v` | Esteira (só sai na direção da seta) | 1 |
| `+` | Bônus | −4 na primeira vez, 1 nas seguintes |
| `*` | Fonte de energia | −2 toda vez |
| `#` | Parede | intransponível |

## 2. Modelagem

<!-- O mapa não é o grafo. -->

- G_pos (grafo de posições): Matriz em que células adjacentes (N, L, S, O) são consideradas navegaveis caso cumpram as regras de navegação (ter a chave, não ser parede...)
- G_est (grafo de estados): É gerado dinamicamente durante a execução dos algoritmos de busca ao iterar pelo grafo de posições, também é gerado uma árvore de caminho reverso para cada mapa a fim de se encontrar o caminho mínimo.
- Rótulo do estado `(linha,coluna)|{chaves}|{bônus}`: Uma representação de uma célula durante a busca pelo menor caminho sobre as restrições e regras impostas pelo problema.
- Nó virtual ALVO: Posição final em que o algoritmo deve encontrar o caminho até ele.
- Por que o grafo é dirigido (esteiras, coleta de chave): Após o algoritmo passar por determinadas células ela apenas pode navegar em uma direção sem poder voltar no estado anterior, a mais clara é no chão direcionado mas o mesmo também ocorre quando é pego uma chave ou numa célula bonûs (+)

## 3. Estruturas de dados

<!-- Tabela hash (dict) e conjunto (set). -->

| Estrutura | Onde é usada | Por que foi escolhida | Custo |
|---|---|---|---|
| Tabela hash (`dict`) | (Árvores de caminho reverso, menor custo encontrado, outros subproblemas envolvendo chave valor) por estados | Menor complexidade de inserção e busca  | Busca, escrita, O(1), Iterar O(n) |
| Conjunto (`set`) | Estados visitados | Menor complexidade de inserção e busca | Busca, escrita, O(1), Iterar O(n) |
| Pilha (`list`) | dfs, backtraking | base do algoritmo de dfs | Push O(1), Pop O(1) |
| Fila (`deque`) | Bfs, Mapa de distância | base do algoritmo de bfs | Enqueue O(1) Dequeue O(1) |
| Fila de prioridade (`heapq`) | Dijstra, A*, Prim | Uso de fila de prioridade | Enqueue O(log(n)) Dequeue O(log(n)) |
| Disjoint Set (`DisjointSet`) | Kruskal | União de conjuntos + consulta | Complexidade O(1) |

- Representação do estado (`MapState`): ((x, y), {keys}, {bonus_visited})
- Representação do grafo (lista de adjacência): list[MapState]
- Exploração a partir do estado inicial, sem gerar todas as combinações: [PREENCHER]

## 4. Gerador de mapas

<!-- Código: src/map/map_generator.py e src/gerar_mapa.py -->

- Etapas da geração (`generate_map`): o gerador monta o mapa em etapas, sempre nesta ordem:
  1. Constrói o labirinto base com a estratégia escolhida. Altura e largura são forçadas a ímpar (`rows |= 1`, `cols |= 1`), e o resultado é uma grade de paredes e corredores, cercada por parede.
  2. Cria ciclos (`generate_loops`): remove paredes internas com probabilidade `braid_factor`. Com 0 o labirinto fica "perfeito" (um único caminho entre duas casas); valores maiores abrem caminhos alternativos.
  3. Sorteia a posição de `S` entre as casas de coordenadas ímpares.
  4. Faz uma BFS a partir de `S` (`get_cells_by_distance`) e guarda as casas na ordem em que são alcançadas, da mais perto para a mais longe.
  5. Distribui as chaves e portas (`generate_key_port`).
  6. Escolhe a posição de `G` (`get_worst_cell`): faz uma BFS sobre pares (posição, chaves coletadas) e escolhe a casa mais distante de `S`, em número de passos, já respeitando as portas.
  7. Distribui as esteiras (`generate_floor_direct`) e os demais terrenos (`generate_floor_variation`).
  8. Calcula as estatísticas do mapa (`compute_stats`), como a contagem de cada tipo de casa.
- Estratégias do labirinto (parâmetro `strategy`):
  - `backtracking`: busca em profundidade com pilha. Parte de uma casa ímpar sorteada, anda de 2 em 2 para um vizinho ainda não visitado, abre a parede do meio e volta atrás quando não há vizinho livre.
  - `recursive_division`: começa com uma sala aberta e a divide recursivamente por paredes, deixando uma passagem em cada parede. Escolhe a direção do corte conforme a proporção da área (vertical se for mais larga do que alta).
  - `kruskal`: cada casa ímpar é um nó e cada parede entre duas casas vizinhas é uma aresta candidata. As arestas são embaralhadas, e a parede só é aberta se as duas casas ainda estiverem em conjuntos diferentes. A verificação usa a estrutura de conjuntos disjuntos (`DisjointSet`, com compressão de caminho e união por rank).
  - `prim`: parte de uma casa sorteada e mantém uma lista de arestas de fronteira. Sorteia uma delas e, se a casa de destino ainda não foi visitada, abre a parede e acrescenta as novas arestas.
- Distribuição de chaves e portas (`generate_valid_sequence`, `generate_key_port`): primeiro sorteia uma sequência em que cada porta só aparece depois da sua chave. Depois coloca os elementos da sequência em posições igualmente espaçadas ao longo da lista da BFS (passo = total de casas ÷ (tamanho da sequência + 2)). Assim as chaves ficam mais perto de `S`, as portas mais longe, e uma chave nunca fica atrás da própria porta. As letras vêm do parâmetro `keys`, e cada chave cria a porta correspondente.
- Esteiras, água, lama, bônus e fonte:
  - Esteiras (`floor_directed_density`): só são colocadas sobre casas de chão comum. As casas por onde passa o caminho de `S` até `G` recebem a direção desse caminho. As que ficam fora do caminho recebem uma direção sorteada entre os vizinhos que não são parede. Casas que o caminho cruza mais de uma vez não recebem esteira.
  - Água, lama, bônus e fonte (`water_density`, `mud_density`, `bonus_density`, `source_density`): cada casa de chão comum sorteia um número entre 0 e 1 e vira um desses terrenos conforme as faixas acumuladas das densidades. A soma de todas as densidades não pode passar de 1, senão o gerador levanta `ValueError`.
- Parâmetros (`GENERATOR_PARAMS`, em `src/gerar_mapa.py`):

| Parâmetro | Significado | Exemplo de entrada |
|---|---|---|
| `rows`, `cols` | tamanho do mapa (linhas × colunas) | 15 × 11 |
| `strategy` | algoritmo que gera o labirinto | `backtracking` |
| `keys` | chaves do mapa; cada uma cria a porta correspondente | `a`, `b`, `c` |
| `braid_factor` | fração de paredes removidas para criar ciclos (0 a 1) | 0.00 |
| `water_density` | fração de casas de água | 0.03 |
| `mud_density` | fração de casas de lama | 0.03 |
| `source_density` | fração de casas de fonte | 0.0 |
| `bonus_density` | fração de casas de bônus | 0.01 |
| `floor_directed_density` | fração de esteiras direcionadas | 0.20 |


### 4.1 Mapas do grupo

Além dos mapas `m01` a `m08` fornecidos pela orientadora, o grupo trabalhou com três mapas extras. Eles foram gerados pelo gerador descrito acima e depois editados à mão: foram colocadas casas de bônus (`+`) e esteiras (`>`, `<`, `^`, `v`) para criar os estados-armadilha.

| Mapa | Arquivo | Origem |
|---|---|---|
| m09 | [`m09_gerado_01.txt`](maps/m09_gerado_01.txt) | gerado por `src/gerar_mapa.py` e editado à mão (bônus e esteiras) |
| m10 | [`m10_gerado_02.txt`](maps/m10_gerado_02.txt) | gerado por `src/gerar_mapa.py` e editado à mão (bônus e esteiras) |
| m11 | [`m11_gerado_extra.txt`](maps/m11_gerado_extra.txt) | gerado por `src/gerar_mapa.py` e editado à mão (bônus e esteiras) |

Requisitos do enunciado para os mapas do grupo: (1) ao menos 3 chaves, esteiras e bônus, com o caminho de menor custo coletando um bônus e passando por uma esteira; (2) um mapa armadilha, com pelo menos 20% dos estados alcançáveis sendo estados-armadilha.

#### Gabarito

O gabarito de cada mapa é o caminho encontrado por cada algoritmo, escrito como a lista de posições `(linha, coluna)` de `S` até `G`. Ele foi gerado com os cinco algoritmos (A*, Bellman-Ford, BFS, DFS e Dijkstra) por `src/metrics/map_solution.py`, e cada algoritmo tem a sua pasta:

| Algoritmo | Pasta | Arquivo do m09 | Arquivo do m10 | Arquivo do m11 |
|---|---|---|---|---|
| A* | [`out/parte1/gabarito_mapa_gerado/astar/`](out/parte1/gabarito_mapa_gerado/astar/) | [`gabarito_m09_gerado_01.txt`](out/parte1/gabarito_mapa_gerado/astar/gabarito_m09_gerado_01.txt) | [`gabarito_m10_gerado_02.txt`](out/parte1/gabarito_mapa_gerado/astar/gabarito_m10_gerado_02.txt) | [`gabarito_m11_gerado_extra.txt`](out/parte1/gabarito_mapa_gerado/astar/gabarito_m11_gerado_extra.txt) |
| Bellman-Ford | [`out/parte1/gabarito_mapa_gerado/bellman_ford/`](out/parte1/gabarito_mapa_gerado/bellman_ford/) | [`gabarito_m09_gerado_01.txt`](out/parte1/gabarito_mapa_gerado/bellman_ford/gabarito_m09_gerado_01.txt) | [`gabarito_m10_gerado_02.txt`](out/parte1/gabarito_mapa_gerado/bellman_ford/gabarito_m10_gerado_02.txt) | [`gabarito_m11_gerado_extra.txt`](out/parte1/gabarito_mapa_gerado/bellman_ford/gabarito_m11_gerado_extra.txt) |
| BFS | [`out/parte1/gabarito_mapa_gerado/bfs/`](out/parte1/gabarito_mapa_gerado/bfs/) | [`gabarito_m09_gerado_01.txt`](out/parte1/gabarito_mapa_gerado/bfs/gabarito_m09_gerado_01.txt) | [`gabarito_m10_gerado_02.txt`](out/parte1/gabarito_mapa_gerado/bfs/gabarito_m10_gerado_02.txt) | [`gabarito_m11_gerado_extra.txt`](out/parte1/gabarito_mapa_gerado/bfs/gabarito_m11_gerado_extra.txt) |
| DFS | [`out/parte1/gabarito_mapa_gerado/dfs/`](out/parte1/gabarito_mapa_gerado/dfs/) | [`gabarito_m09_gerado_01.txt`](out/parte1/gabarito_mapa_gerado/dfs/gabarito_m09_gerado_01.txt) | [`gabarito_m10_gerado_02.txt`](out/parte1/gabarito_mapa_gerado/dfs/gabarito_m10_gerado_02.txt) | [`gabarito_m11_gerado_extra.txt`](out/parte1/gabarito_mapa_gerado/dfs/gabarito_m11_gerado_extra.txt) |
| Dijkstra | [`out/parte1/gabarito_mapa_gerado/dijkstra/`](out/parte1/gabarito_mapa_gerado/dijkstra/) | [`gabarito_m09_gerado_01.txt`](out/parte1/gabarito_mapa_gerado/dijkstra/gabarito_m09_gerado_01.txt) | [`gabarito_m10_gerado_02.txt`](out/parte1/gabarito_mapa_gerado/dijkstra/gabarito_m10_gerado_02.txt) | [`gabarito_m11_gerado_extra.txt`](out/parte1/gabarito_mapa_gerado/dijkstra/gabarito_m11_gerado_extra.txt) |

Os mesmos arquivos existem para `m01` a `m08`, com duas exceções. O `m07` não tem arquivo em nenhuma pasta, porque o mapa não tem solução. O `m06` não tem arquivo no Bellman-Ford (que detecta o ciclo negativo e levanta erro) nem no Dijkstra (que não termina nesse mapa).

## 5. Algoritmos

<!-- Código: src/solver/ -->

| Algoritmo | Critério | Estrutura | Complexidade |
|---|---|---|---|
| BFS | Menor número de passos (arestas), sem olhar o custo. Expande os estados por nível, do mais perto ao mais longe de `S`. | Fila FIFO (`deque`) e tabela hash (`dict`) de predecessores, que também marca os estados já visitados. | O(V + E) |
| DFS | Segue um caminho até o fim antes de voltar. Devolve o primeiro caminho que encontra, sem garantia de ser o menor. | Pilha LIFO (`list`) e tabela hash (`dict`) de predecessores. | O(V + E) |
| Dijkstra | Menor custo acumulado desde `S`. Sempre expande o estado de menor custo conhecido. | Fila de prioridade (`heapq`, min-heap) e tabela hash (`dict`) com o melhor custo e o predecessor de cada estado. | O((V + E) log V) |
| Bellman-Ford | Menor custo acumulado, relaxando todas as arestas em até V − 1 rodadas. Uma rodada extra detecta ciclo negativo. | Conjunto (`set`) de todos os estados alcançáveis, obtido por exploração prévia, e tabela hash (`dict`) com custos e predecessores. | O(V · E) |
| A* | Menor custo, guiado por uma estimativa. A prioridade é custo acumulado + heurística (distância de Manhattan até `G`). | Fila de prioridade (`heapq`) e tabela hash (`dict`) com o melhor custo e o predecessor. | O((V + E) log V) no pior caso, o mesmo do Dijkstra. |

V e E são o número de estados e de arestas do grafo de estados (G_est) alcançável a partir de `S`.

### 5.1 Discussões obrigatórias

- m01 — por que BFS e Dijkstra dão caminhos diferentes: [PREENCHER]
- m05 — por que o G_est não tem ciclo negativo (prova): [PREENCHER]
- m06 — ciclo negativo e correção da regra da fonte: [PREENCHER]
- m07 — por que não há solução e quantos estados são alcançáveis: [PREENCHER]

### 5.2 Estados-armadilha

- Definição e como são calculados: [PREENCHER]
- Resultados (m04, m07): [PREENCHER]

## 6. Métricas

<!-- Código: src/metrics/graph_metrics.py e src/metrics/state_degrees.py -->

- Definições: ordem, tamanho, densidade, teto teórico e taxa de ocupação: [PREENCHER]
- Graus de entrada e de saída: [PREENCHER]

### 6.1 Resultados por mapa

| Mapa | Ordem G_pos | Tamanho G_pos | Densidade G_pos | Ordem G_est | Tamanho G_est | Densidade G_est | Teto | Ocupação |
|---|---|---|---|---|---|---|---|---|
| m01 | [PREENCHER] | | | | | | | |
| m02 | [PREENCHER] | | | | | | | |
| ... | | | | | | | | |

### 6.2 Camadas e arcos entre camadas

- Subgrafos por conjunto de chaves: [PREENCHER]
- Arcos entre camadas e as casas que os geram: [PREENCHER]

### 6.3 Graus e multiplicidade

- Estado com maior grau de saída e de entrada: [PREENCHER]
- Multiplicidade máxima de uma casa (m08): [PREENCHER]

## 7. Testes

### 7.1 Como executar

```bash
python3 -m pytest test/map_loader test/test_algorithms -v
```

### 7.2 Casos testados

| Grupo | Caso | Resultado esperado | Resultado |
|---|---|---|---|
| map_loader (leitura) | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| map_loader (ida e volta) | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| BFS | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Dijkstra | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Bellman-Ford | [PREENCHER] | [PREENCHER] | [PREENCHER] |

- Cobertura e limitações dos testes: [PREENCHER]

## 8. Visualizações

> Para cada figura: o que mostra, qual insight, por que esse tipo de gráfico.
> Título, legenda e rótulos de eixo são obrigatórios.

### 8.1 Algoritmos escolhidos

- Algoritmos exibidos (até 4) e motivo da escolha: [PREENCHER]

### 8.2 Heatmap das camadas

![Heatmap das camadas](out/parte1/figuras/heatmap_camadas.png)

- O que mostra: [PREENCHER]
- Insight: [PREENCHER]
- Por que este gráfico: [PREENCHER]

### 8.3 Heatmap de acessos por casa (G_pos)

![Heatmap de acessos por casa](out/parte1/figuras/heatmap_acessos.png)

- O que mostra: [PREENCHER]
- Insight: [PREENCHER]
- Por que este gráfico: [PREENCHER]

### 8.4 Árvore BFS dos estados

![Árvore BFS dos estados](out/parte1/figuras/arvore_bfs.png)

- O que mostra: [PREENCHER]
- Insight: [PREENCHER]
- Por que este gráfico: [PREENCHER]

### 8.5 Métricas resumo

![Métricas resumo](out/parte1/figuras/metricas_resumo.png)

| Algoritmo | Estados expandidos | Passos | Custo | Tempo |
|---|---|---|---|---|
| [PREENCHER] | | | | |

- Interpretação: [PREENCHER]

## 9. Conclusão e limitações

- Conclusões: [PREENCHER]
- Limitações: [PREENCHER]
- Possíveis melhorias: [PREENCHER]

## 10. Apêndices

### 10.1 Gabarito dos mapas do grupo

| Mapa | Nº de estados | Nº de arcos | Passos (BFS) | Custo (Dijkstra ou Bellman-Ford) |
|---|---|---|---|---|
| [PREENCHER] | | | | |

### 10.2 Matriz de contribuição

| Integrante | Pacotes de trabalho | Dono / revisor |
|---|---|---|
| [PREENCHER] | | |

### 10.3 Uso de IA

- Trechos feitos com apoio de IA e finalidade: [PREENCHER]
- Declaração de Uso de IA assinada (`docs/`): [PREENCHER]

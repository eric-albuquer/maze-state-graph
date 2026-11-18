# Relatório — Parte 1: Labirinto com Chaves (Grafo de Estados)

Teoria dos Grafos + AVD — 2026.2

> Esqueleto de tópicos. Cada seção traz o que deve ser coberto e um espaço `[PREENCHER]`.
> O texto, as análises e as conclusões devem ser escritos pelo grupo.

**Integrantes:** [PREENCHER]

**Orientador(a):** [PREENCHER]

---

## 1. Introdução

<!-- Problema, objetivo e visão geral do projeto. -->

- Descrição do problema (S, G, chaves, portas, terrenos): [PREENCHER]
- Mapas utilizados (m01 a m08 e mapas do grupo): [PREENCHER]
- Tabela de custos por terreno: [PREENCHER]

## 2. Modelagem

<!-- O mapa não é o grafo. -->

- G_pos (grafo de posições): [PREENCHER]
- G_est (grafo de estados): [PREENCHER]
- Rótulo do estado `(linha,coluna)|chaves|{bônus}`: [PREENCHER]
- Nó virtual ALVO: [PREENCHER]
- Por que o grafo é dirigido (esteiras, coleta de chave): [PREENCHER]
- Ordem dos vizinhos (N, L, S, O): [PREENCHER]

## 3. Estruturas de dados

<!-- Tabela hash (dict) e conjunto (set). -->

| Estrutura | Onde é usada | Por que foi escolhida | Custo |
|---|---|---|---|
| Tabela hash (`dict`) | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Conjunto (`set`) | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Outras (pilha, fila, heap) | [PREENCHER] | [PREENCHER] | [PREENCHER] |

- Representação do estado (`MapState`): [PREENCHER]
- Representação do grafo (lista de adjacência): [PREENCHER]
- Exploração a partir do estado inicial, sem gerar todas as combinações: [PREENCHER]

## 4. Gerador de mapas

<!-- Código: src/map/map_generator.py e src/gerar_mapa.py -->

- Etapas da geração: [PREENCHER]
- Estratégias do labirinto (backtracking, divisão recursiva, Kruskal, Prim): [PREENCHER]
- Distribuição de chaves e portas: [PREENCHER]
- Esteiras, água, lama, bônus e fonte: [PREENCHER]
- Parâmetros (`GENERATOR_PARAMS`): [PREENCHER]
- Como o mapa é salvo (`map_save`) e recarregado (`map_load`): [PREENCHER]

### 4.1 Mapas do grupo

| Mapa | Requisito | Como foi obtido | Como foi validado |
|---|---|---|---|
| Mapa 1 | ≥ 3 chaves, esteiras e bônus; caminho de menor custo coleta bônus e passa por esteira | [PREENCHER] | [PREENCHER] |
| Mapa armadilha | ≥ 20% dos estados alcançáveis são armadilha | [PREENCHER] | [PREENCHER] |

## 5. Algoritmos

<!-- Código: src/solver/ -->

| Algoritmo | Critério | Estrutura | Complexidade | Peso negativo |
|---|---|---|---|---|
| BFS | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| DFS | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Dijkstra | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Bellman-Ford | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| A* | [PREENCHER] | [PREENCHER] | [PREENCHER] | [PREENCHER] |

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

# Labirinto com Chaves (Grafo de Estados) + Comparação de Algoritmos

Projeto final de Teoria dos Grafos + Análise e Visualização de Dados (AVD) — 2026.2.

Resolve labirintos com chaves e portas modelando o problema como um **grafo de
estados** (posição + chaves coletadas) e busca o caminho de menor custo entre
`S` (início) e `G` (fim).

## Requisitos

- Python 3.11+
- [pygame](https://www.pygame.org/) (visualização/UI)

```bash
pip install -r requirements.txt
```

> Não é permitido usar bibliotecas que já implementem BFS/DFS/Dijkstra/Bellman-Ford
> (networkx, igraph, graph-tool). O networkx só pode ser usado dentro dos testes,
> como oráculo para conferir resultados.

## Estrutura

```
.
├── src/
│   ├── ui.py               # interface gráfica (pygame)
│   ├── visualizations.py   # árvore de busca (layout + tela)
│   ├── sprites.py          # carregamento/cache dos sprites
│   ├── gerar_mapa.py       # script que gera e salva um mapa aleatório
│   ├── map/                # modelo do mapa
│   │   ├── map.py
│   │   ├── map_nodes.py        # tipos de célula (parede, chave, porta...)
│   │   ├── map_state.py        # estado do grafo (posição + chaves)
│   │   ├── map_loader.py       # leitura/gravação de mapas
│   │   └── map_generator.py    # gerador de mapas
│   ├── solver/             # algoritmos de busca no grafo de estados
│   │   ├── solver_common.py    # vizinhança/transições comuns
│   │   ├── solver_solution.py  # resultado (iterações, caminho, mensagem)
│   │   ├── bfs_solver.py
│   │   ├── dfs_solver.py
│   │   ├── dijkstra_solver.py
│   │   ├── bellman_ford_solver.py
│   │   ├── astar_solver.py
│   │   ├── wall_solver.py      # caminhada pelas paredes
│   │   ├── xiter_solver.py     # A* Hack
│   │   ├── random_walk.py
│   │   └── portal_solver.py
│   ├── metrics/            # métricas do grafo e gabaritos (Parte 1)
│   │   ├── get_map_states.py
│   │   ├── state_degrees.py    # graus dos estados (CSV)
│   │   ├── graph_metrics.py    # métricas dos grafos
│   │   └── map_solution.py     # gabaritos por algoritmo
│   └── settings/           # configurações
│       ├── display.py          # cores/FPS da UI
│       ├── map_setup.py        # lista e escolha de mapas
│       └── solver_setup.py     # algoritmos disponíveis na UI
├── test/                   # testes (pytest)
│   ├── map_loader/
│   ├── test_algorithms/
│   ├── test_degrees.py
│   ├── test_generator.py
│   └── test_tree_layout.py
├── maps/                   # mapas m01 a m11
├── sprites/                # imagens usadas pela UI
├── out/parte1/             # saídas geradas (graus, métricas, gabaritos)
├── docs/                   # enunciado, critérios e declaração de IA
├── relatorio.md            # relatório do projeto
└── requirements.txt
```

## Como executar

Execute sempre a partir da raiz do projeto (os mapas são lidos de `maps/`).

```bash
python -m src.ui                    # interface gráfica
python -m src.gerar_mapa            # gera um mapa aleatório em maps/
python -m src.metrics.graph_metrics # gera out/parte1/metricas_grafos.txt
python -m src.metrics.map_solution  # gera os gabaritos em out/parte1/gabarito_mapa_gerado/
```

Algoritmos disponíveis na UI: A\*, BFS, DFS, Dijkstra, Bellman-Ford, BFS Wall
(caminhada pelas paredes), A\* Hack, Random Walk e Portal Solver.

## Testes

```bash
python -m pytest                                  # todos os testes
python -m pytest test/test_algorithms/test_bfs.py # um arquivo específico
python -m pytest test/test_algorithms/test_dfs.py # testes do DFS
python -m pytest test/test_algorithms/test_dijkstra.py # testes do Dijkstra
python -m pytest test/test_algorithms/test_bellman_ford.py # testes do Bellman-Ford
```

## Formato dos mapas

Arquivos de texto em `maps/`, um caractere por célula:

| Símbolo | Significado |
|---------|-------------|
| `#` | parede |
| `.` | chão (custo 1) |
| `S` / `G` | início / fim |
| `a`–`z` | chave |
| `A`–`Z` | porta correspondente à chave |
| `,` | lama |

Os demais terrenos (água, esteiras direcionadas, bônus, fonte) estão definidos em
`src/map/map.py`; veja `maps/m01` a `m11` para exemplos.

## Entrega

- Repositório no GitHub (enviar só o link no Classroom).
- Incluir código, mapas, dataset (ou script de download), README, PDF
  (manual + técnica) e `docs/DECLARACAO_IA.pdf` assinada.
- Grupos de 4 ou 5 integrantes; PDF com matriz de contribuição.

| Etapa | Data |
|-------|------|
| Proposta do dataset da Parte 2 | até 12/10/2026 |
| Acompanhamentos (Grafos) | 10/11, 17/11, 19/11, 24/11 |
| Acompanhamentos (AVD) | 17/11, 19/11, 24/11 |
| Entrega do material | 26/11/2026 |
| Apresentações | 26/11 (turma A), 01/12 (turma B), 03/12 (remanescentes) |

## Declaração de uso de IA

[Documento de declaração de uso de IA](https://docs.google.com/document/d/1a_AzeSNbBuQOpufTuFRQ0rQSwkhV5YSE/edit?usp=sharing&ouid=115450337528857953689&rtpof=true&sd=true)

## Integrantes

Amanda Luz
Caio Almeida
Eric Albuquerque
Gabriel Aniceto
Mircio Ferreira

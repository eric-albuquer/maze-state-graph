# Labirinto com Chaves (Grafo de Estados) + Comparação de Algoritmos

Projeto final de Teoria dos Grafos + Análise e Visualização de Dados (AVD) — 2026.2.

Resolve labirintos com chaves e portas modelando o problema como um **grafo de
estados** (posição + chaves coletadas) e busca o caminho de menor custo entre
`S` (início) e `G` (fim).

## Requisitos

- Python 3.11+
- [pygame](https://www.pygame.org/) (visualização/UI)

```bash
pip install pygame
```

> Não é permitido usar bibliotecas que já implementem BFS/DFS/Dijkstra/Bellman-Ford
> (networkx, igraph, graph-tool). O networkx só pode ser usado dentro dos testes,
> como oráculo para conferir resultados.

## Estrutura

```
.
├── map/        # modelo do mapa, leitura/gravação e gerador de mapas
│   ├── map.py
│   ├── map_loader.py
│   └── map_generator.py
├── solver/     # solução do labirinto (grafo de estados)
│   └── solver.py
├── test/       # testes
│   └── test.py
├── maps/       # mapas m01 a m08
└── ui.py       # interface gráfica
```

## Como executar

Execute sempre a partir da raiz do projeto (os mapas são lidos de `maps/`
relativo ao diretório atual).

```bash
python -m src.ui            # interface gráfica
python -m test.test     # testes
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
`map/map.py`; veja `maps/m01` a `m08` para exemplos.

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

## Integrantes

Amanda Luz
Caio Almeida
Eric Albuquerque
Gabriel Aniceto
Mircio Ferreira

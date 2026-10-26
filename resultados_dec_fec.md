# Resultados — DEC/FEC e eventos (2023–2026)

> EDA, tratamento e leitura dos indicadores de continuidade da Eletropaulo.
> Data: 26/10/2026.

---

## 1. O que foi tratado

| Problema encontrado no EDA | Tratamento |
|---|---|
| `BANDEIRANTES` (2020–2023) e `NOVO BANDEIRANTES` (2024–2026) são o mesmo conjunto renomeado | unificados |
| 2026 tem apenas **5 meses** (o resto do ano não existia no arquivo) | marcado `parcial = True`, fora das séries anuais |
| 143 conjuntos, dos quais **21 são de outros municípios** da concessão | coluna `municipio`; a série usa só os **122 da capital** |
| indicador anual | **soma dos 12 meses** (os mensais são incrementos) |

Saída: `data/processed/dec_fec_tratado.csv` (572 linhas = 143 conjuntos × 4 anos).

## 2. O achado central

O DEC mediano da capital **caiu** entre 2023 e 2025:

| Ano | mediana | p90 | máx |
|---|---|---|---|
| 2023 | 6,18 h | 9,55 h | 19,34 h |
| 2024 | 5,97 h | 8,97 h | 15,67 h |
| 2025 | 5,95 h | 9,19 h | 15,90 h |
| 2026 | — | — | — (5 meses, não comparável) |

No papel, o serviço **melhorou levemente** justamente no período em que a concessionária entrou em crise e a caducidade foi aberta.

Enquanto isso, no arquivo de eventos de 2025 (473.301 registros após deduplicação):

- mediana de **3,57 h** por interrupção;
- p95 de **21,1 h**;
- **16.354** quedas acima de 24 h (3,5% do total);
- **3.950** acima de 48 h e **1.366** acima de 72 h;
- a maior durou **168,8 h — sete dias**.

**A média não se move; a cauda se aprofunda.** É a hipótese do silenciamento das métricas aparecendo no dado: o indicador agregado é indiferente a um universo de eventos severos que ele não incorpora.

## 3. O FEC conta outra parte da história

O FEC mede **quantas vezes** a luz caiu; o DEC, **por quanto tempo**. Em 2025, na capital, a mediana é de **2,95 quedas** por ano, e os 10% piores passam de **5,93**.

DEC e FEC têm correlação de **0,85** — andam juntos, mas não são a mesma coisa. O caso que mostra a diferença é **Raposo Tavares**: 14,5 h de DEC (alto, mas não o maior) e **18,7 quedas** de FEC, quase o dobro do segundo colocado. É o conjunto onde a luz cai com mais frequência em toda a capital.

Isso importa para o argumento: um território pode ter poucas horas totais de escuridão e ainda assim uma experiência de **instabilidade crônica** — a luz que volta e cai, queima geladeira, interrompe trabalho. O DEC sozinho não vê isso.

## 4. Onde a escuridão se concentra (capital, 2025)

Vargem Grande (15,9 h), Parelheiros (15,5), Raposo Tavares (14,5), Rio Grande (13,7), Varginha (13,6), Parque dos Lagos (10,3), Santa Maria (10,1), Rio Bonito (9,9), Vila Almeida (9,7), Vila Ema (9,6).

Todos fora do centro expandido. O ranking repete, no indicador oficial, o padrão que o Censo mostra na composição racial — mas isso só pode ser afirmado com o crosswalk.

## 5. Cuidados de leitura (para o texto)

1. **DEC ≠ duração de evento.** O DEC é uma média por unidade consumidora dentro do conjunto; a duração é de cada interrupção. Comparar os dois diretamente é erro de método. O contraste válido é entre **o que o índice registra** e **o que o arquivo de eventos mostra**.
2. **Recortes diferentes.** A série de DEC é da **capital** (122 conjuntos); os números de eventos são da **concessão inteira** (143 conjuntos, ~24 municípios). A anotação do gráfico diz "da concessão" por isso.
3. **2026 não entra em série anual.** Cinco meses não se comparam com doze.
4. **A queda do DEC não é boa notícia.** Ela convive com o aumento da severidade dos eventos — o que sugere que o indicador mede outra coisa.
5. **Crosswalk ainda pendente.** Sem ele, não se cruza DEC com distrito, raça ou saneamento.

---

## Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `data/processed/dec_fec_tratado.csv` | painel conjunto × ano, com flags de parcial e município |
| `data/processed/eventos_eletropaulo_2025.csv` | 473 mil eventos com duração calculada |
| `data/processed/figures/dec_01_indicador_parado.png` | o índice plano contra a crise |
| `data/processed/figures/dec_02_concentracao.png` | ranking de DEC 2025 na capital |
| `data/processed/figures/dec_03_cauda.png` | distribuição das durações, com a cauda em destaque |
| `data/processed/figures/dec_04_frequencia_duracao.png` | DEC × FEC: duração e frequência não coincidem |
| `data/processed/figures/dec_05_fec_ranking.png` | ranking de FEC 2025 na capital |
| `src/dec_fec_pipeline.py` | tratamento |
| `src/eventos_pipeline.py` | eventos |
| `src/graficos_dec_fec.py` | figuras |

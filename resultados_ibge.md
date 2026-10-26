# Resultados — Censo 2022 por distrito (São Paulo)

> O que o EDA dos três arquivos do IBGE mostrou, e o que isso permite afirmar no TCC.
> Data: 26/10/2026.

---

## 1. O que foi verificado

- **96 distritos** da capital, **população 11.451.999** — confere com o Censo 2022.
- Encoding **latin-1**, separador `;`, decimal com vírgula.
- `basico` usa `v0001` (minúsculo); os demais usam `V0001` (maiúsculo) — confundir os dois troca numerador por denominador.
- **Nenhum `x`** (sigilo estatístico) nos blocos usados, na capital: não há supressão no grão do distrito em São Paulo.

## 2. O achado que muda a estratégia

A variável forte é **cor/raça**. As variáveis de saneamento estão **saturadas**:

| Indicador | mín | mediana | máx |
|---|---|---|---|
| % população preta + parda | 9,9 | 40,8 | 65,0 |
| % domicílios sem rede de água | 0,00 | 0,15 | 64,7* |
| % domicílios sem banheiro | 0,00 | 0,00 | 0,13 |
| % domicílios sem coleta de lixo | 0,00 | 0,07 | 2,58 |

\* Marsilac, o único distrito com área rural relevante. Sem ele, o máximo cai para ~10% (Parelheiros).

**Isso não é um problema — é um argumento.** A cidade alcançou a **universalidade formal** de água, banheiro e coleta. O que sobra de desigualdade não está no **acesso** à infraestrutura, mas na **qualidade e na continuidade** dela. É exatamente a tese do Anand: estar conectado não é estar servido. O DEC/FEC mede justamente essa camada — a da confiabilidade — e é aí que a clivagem racial aparece.

Em outras palavras: se o TCC fosse sobre "quem tem energia", não haveria desigualdade a mostrar. Ele é sobre "**quem fica sem energia, e por quanto tempo**". O dado do Censo sustenta essa escolha.

## 3. Correlações com % de população negra (Spearman)

| Variável | ρ |
|---|---|
| % domicílios sem coleta de lixo | **0,75** |
| População total do distrito | 0,57 |
| % domicílios sem rede de água | 0,54 |
| % domicílios sem banheiro | 0,39 |

O lixo é o indicador de saneamento que ainda discrimina. A correlação com população reflete o padrão periférico: os distritos mais negros são também os mais populosos.

## 4. Os extremos

**Maior população negra:** Jardim Ângela (65,0%), Grajaú (62,1%), Jardim Helena (61,6%), Cidade Tiradentes (61,6%), Lajeado (61,1%), Parelheiros (61,0%).

**Menor:** Moema (9,9%), Alto de Pinheiros (10,0%), Jardim Paulista (11,2%), Itaim Bibi (11,3%), Pinheiros (11,4%), Vila Mariana (11,5%).

A razão entre os extremos é de **6,5 vezes**. Não é uma gradação suave: é uma cidade partida.

---

## 5. O que ainda falta para fechar a análise

1. **A ponte conjunto → distrito** (crosswalk). Sem ela, o DEC/FEC não se junta ao Censo. É o único passo que impede os gráficos centrais (DEC × raça).
2. **Renda** não existe no Universo — ver `fontes_ibge.md` §1.3. Alternativas: proxies, Mapa da Desigualdade (secundária) ou microdados da Amostra.
3. **Variáveis que valeria baixar** (`caracteristicas_domicilio1`, 89 variáveis): traz `V00001` (DPPO exato, denominador exato), `V00050` (% cortiço) e `V00052` (estrutura degradada) — dois proxies de precariedade que discriminam melhor que banheiro.

---

## 6. Como usar isso no texto do desenvolvimento

- A figura dos extremos serve para **estabelecer o recorte socioespacial** antes de falar de energia: a cidade já está partida em dois mundos quando a luz cai.
- A saturação do saneamento deve ser **dita explicitamente**, e não escondida. Ela fortalece a tese: a desigualdade migrou do acesso para a continuidade.
- Cuidado com **Marsilac**: é rural, distorce qualquer média de infraestrutura. Tratar como caso à parte ou excluir, declarando a decisão.
- **Correlação não é causação.** O dado mostra coincidência espacial; o mecanismo vem da etnografia e da literatura.

---

## Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `data/processed/ibge_distritos_sp.csv` | 96 distritos com população, área, densidade e os 4 indicadores |
| `data/processed/figures/ibge_01_extremos_populacao_negra.png` | os dois extremos da cidade |
| `data/processed/figures/ibge_02_negro_x_lixo.png` | dispersão % negro × lixo sem coleta |
| `src/ibge_pipeline.py` | tratamento (reprodutível) |
| `src/graficos_ibge.py` | figuras |

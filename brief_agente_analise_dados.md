# Brief para o agente de análise de dados
## TCC de Ciências Sociais — Falhas de energia elétrica em São Paulo (Enel/Eletropaulo)

> Passagem de bastão. Escrito a partir da introdução do TCC ("A infraestrutura como Arena de Poder", recorte 2023–2026). Destina-se a um **agente de análise de dados** que vai trabalhar **dentro deste repositório**. Data: 02/10/2026.

---

## 0. Ambiente de trabalho e o que se espera de você

**A pasta de trabalho é este repositório (`tcc_energia_2026`), aberto no VSCode.** A pasta `tcc_cs_unifesp` **não estará disponível** — ignore qualquer caminho fora do repo. **Todos os caminhos neste documento são relativos à raiz do repo.**

Seu trabalho é um **ciclo de análise de dados em três fases** (detalhado na seção 3):
1. **Análise/diagnóstico inicial** do dado bruto (EDA exploratória).
2. **Tratamento/limpeza** (produzir dataset tratado).
3. **EDA e análise de dados** sobre o tratado (as métricas e os gráficos finais).

O objetivo final **não** é um relatório denso: são **gráficos claros e objetivos** que contam a história do TCC (seção 1), acompanhados de **datasets tratados e reprodutíveis** e do **código versionado**.

---

## 1. A história que os gráficos precisam contar

O TCC é de Ciências Sociais, com virada **antropológica** e método de **"etnografia de dados"**: as métricas não são rejeitadas, mas tratadas como objeto — lê-se o que elas medem **e o que apagam**. O eixo é a **experiência/vivência**; os dados entram como **contexto e contraponto**.

A narrativa, em uma frase, que cada gráfico deve reforçar:

> A escuridão em São Paulo não é aleatória nem meramente climática: ela se **concentra na periferia** e a **métrica oficial que deveria medi-la a esconde**. O vendaval de novembro de 2023 não criou esse problema — ele **revelou** uma negligência estrutural.

Dois alvos analíticos:

**H1 — Geometria de poder infraestrutural.** DEC (horas sem luz) e FEC (nº de quedas) não se distribuem ao acaso: segue-se uma seletividade espacial que prioriza resiliência nas áreas centrais/de elite e nos enclaves fortificados, relegando a periferia a tempos prolongados de abandono elétrico.
→ Gráficos de distribuição espacial e de cruzamento com renda e cor/raça.

**H2 — Silenciamento das métricas.** O indicador agregado (DEC/FEC oficial) subestima a precariedade periférica, diluindo os tempos reais de restabelecimento nas médias por conjunto.
→ Gráficos do **hiato** entre o índice oficial e a experiência medida evento a evento.

**Regra de ouro dos gráficos:** um gráfico = uma mensagem. O título deve ser a mensagem, não o nome do eixo. Eixos rotulados **com unidade** (h/ano, vezes/ano, h). Legível em preto e branco. Anotar o outlier que conta a história (ex.: os 168,8 h = 7 dias). Nada de "média de médias" apresentada como experiência — a experiência mora na **cauda longa**.

---

## 2. Dados: onde estão e como deixá-los prontos no repo

| Arquivo (caminho no repo) | Conteúdo | Tamanho | Situação atual |
|---|---|---|---|
| `data/raw/indicadores-continuidade-coletivos-2020-2029.csv` | Indicadores coletivos DEC/FEC por conjunto, 2020–2026, 105 agentes | ~511 MB | **só ponteiro Git-LFS** (134 bytes) — rodar `git lfs pull` (precisa de `git-lfs` instalado) |
| `data/raw/interrupcoes-energia-eletrica-2025.csv` | Eventos de interrupção (nível de evento), 2025, Brasil inteiro | ~2,9 GB | **ausente** — baixar do portal ANEEL (abaixo) e colocar em `data/raw/` |

**Onde baixar o arquivo de eventos:** portal de dados abertos da ANEEL — `https://dadosabertos.aneel.gov.br` → conjunto *"Interrupções de energia elétrica"* (arquivo anual `interrupcoes-energia-eletrica-2025.csv`). O de indicadores é o conjunto *"Indicadores de Continuidade Coletivos"*.

**Apoio normativo (baixar também):**
- **PRODIST Módulo 8** — o que conta como interrupção, limites, expurgos: `https://www2.aneel.gov.br/cedoc/aren2021956_2_7.pdf`.
- **`dominio-indicadores.csv`** — arquivo à parte da ANEEL com a descrição completa de cada sigla de `SigIndicador` (os 22 códigos da seção 4.1). Sem ele a semântica dos recortes fica no chute.
- **Dicionário de metadados** já presente em `dicionario_aneel/dm-indicadores-continuidade.pdf`.

---

## 3. Fluxo de trabalho em três fases

### Fase 1 — Análise / diagnóstico inicial (dado bruto)
EDA exploratória **sem tratar**: entender o que existe antes de mexer.
- Ler os dois arquivos com os **encodings e separadores corretos** (seção 5) e `nrows`/`chunks` para não estourar a memória.
- Levantar: nº de linhas, agentes, anos, valores distintos de `SigIndicador`, `SigAgente`, `DscTipoInterrupcao`; tipos/andamento de nulos; duplicatas exatas; o problema da `;`-dentro-de-aspas; faixas de datas e de duração (inclusive durações negativas ou absurdas).
- **Saída:** um notebook `notebooks/01_diagnostico.ipynb` + uma lista curta e explícita dos **problemas a tratar** (com contagens). Isso vira o roteiro da Fase 2.

### Fase 2 — Tratamento / limpeza
Aplicar cada correção da seção 5 e gerar o dataset **tratado (tidy)**.
- Encodings certos; parser com aspas; deduplicação; conversão de tipos/datas; vírgula decimal; anualização (soma); separação de anos; recorte do agente e da capital; join conjunto→distrito.
- **Saída:** um script versionado `src/tratamento.py` **e** os CSVs tratados em `data/processed/` (seção 7). Nada de tratamento "na mão" dentro de um gráfico — o tratamento tem de ser reproduzível a partir do bruto.

### Fase 3 — EDA e análise de dados (sobre o tratado)
Ler o tratado e produzir as métricas e os **gráficos da seção 8**.
- Refazer a EDA sobre o dado limpo (distribuições, assimetria, ranking, correlações) e então construir as figuras que sustentam H1 e H2.
- **Saída:** `notebooks/02_analise.ipynb` + as figuras finais em `data/processed/figures/`.

> As figuras antigas em `data/processed/figures/` (`01_histograma_dec_fec.png`, `01_scatter_matriz_vulnerabilidade.png`, `02_boxplot_customizado.png`, `03_barras_divergentes.png`, `04_error_bars.png`) contêm os erros da seção 10 (média tratada como anual, anos misturados, geocodificação por nome). **Servem de referência do que não repetir** — substitua-as.

---

## 4. Dicionário de dados (verificado contra os arquivos reais)

### 4.1. Indicadores coletivos — `indicadores-continuidade-*.csv`
Separador `;`, aspas `"`, **encoding `utf-8-sig`**. Colunas: `DatGeracaoConjuntoDados`, `IdeConjUndConsumidoras`, `DscConjUndConsumidoras`, `SigAgente`, `NumCNPJ`, `SigIndicador`, `AnoIndice` (string), `NumPeriodoIndice` (1–12), `VlrIndiceEnviado` (**vírgula decimal**; zero = `,00`).

**REGRA CRÍTICA — soma, não média.** Os valores mensais são **incrementos do mês**. O **indicador anual = SOMA dos 12 meses**. Tratar a média mensal como valor anual foi o erro do pipeline anterior (dava ≈ 0,58 h quando o anual é ≈ 6–7 h).

**`SigIndicador` — 22 códigos:** `DEC`, `FEC` e os sufixos `IP`, `IPC`, `IND`, `INC`, `INE`, `INO`, `XN`, `XNC`, `XP`, `XPC` (ex.: `DECINE`, `FECXPC`). Esses recortes isolam partes do cálculo (inclusões/exclusões/expurgos). **A semântica de cada sigla vem do `dominio-indicadores.csv` + PRODIST Módulo 8 — não inferir do número.** Exemplo do que revela: em PARELHEIROS/2025 o DEC anual é 15,47 h, mas `DECINE` = 40,16 h e `DECINC` = 6,65 h — matéria-prima direta de H2.

### 4.2. Interrupções (nível de evento) — `interrupcoes-energia-eletrica-2025.csv`
Separador `;`, aspas `"`, **encoding `latin-1` (ISO-8859-1)**. 18 colunas:

| Campo | Uso |
|---|---|
| `DatGeracaoConjuntoDados` | metadado |
| `IdeConjuntoUnidadeConsumidora` | id do conjunto |
| `DscConjuntoUnidadeConsumidora` | nome do conjunto |
| `DscAlimentadorSubestacao` | alimentador |
| `DscSubestacaoDistribuicao` | **subestação** (âncora geográfica mais estável que o conjunto) |
| `NumOrdemInterrupcao` | nº de ordem (**se repete — deduplicar**) |
| `DscTipoInterrupcao` | `Programada` / `Não Programada` |
| `IdeMotivoInterrupcao` | código do motivo |
| `DatInicioInterrupcao` / `DatFimInterrupcao` | início/fim → **duração = fim − início** |
| `DscFatoGeradorInterrupcao` | fato gerador descritivo (**contém `;` dentro das aspas**) |
| `NumNivelTensao` | tensão em volts (240, 13800, ...) |
| `NumUnidadeConsumidora` | **nº de unidades afetadas no evento** |
| `NumConsumidorConjunto` | total de consumidores do conjunto |
| `NumAno` | ano (string) |
| `NomAgenteRegulado` / `SigAgente` / `NumCPFCNPJ` | agente |

---

## 5. Pegadinhas técnicas obrigatórias

1. **Encoding trocado:** eventos = `latin-1`; indicadores = `utf-8-sig` (usar `latin-1` nos indicadores gera mojibake: "Jaçanã").
2. **`;` dentro das aspas** em `DscFatoGeradorInterrupcao` → parser **ingênuo de `;` quebra**. Ler com `quotechar='"'`. Nas linhas da Eletropaulo isso é frequente (`"INTERNA;NAO PROGRAMADA;..."`), a ponto de um split ingênuo **não encontrar** a ELETROPAULO (as colunas deslocam).
3. **`NumOrdemInterrupcao` se repete** → ~33 mil linhas exatamente duplicadas em 2025, até 38 linhas para a mesma ordem. **Deduplicar antes de reconstruir indicadores.**
4. **Soma vs. média** (item 4.1) — o erro conceitual mais grave.
5. **Não misturar anos:** 2025 (12 meses) ≠ 2026 (parcial).
6. **Vírgula decimal** em `VlrIndiceEnviado`; zero = `,00`.
7. **Padding de espaços** em `SigAgente`/`SigIndicador` (`"ELETROPAULO         "`) → `.str.strip()` antes de filtrar.
8. **Eventos são nacionais (2,9 GB, ~9,7 mi de linhas):** filtrar `SigAgente` em `chunks`; nunca carregar inteiro.

**Teste de sanidade (Eletropaulo/2025):** 474.435 eventos brutos (pré-dedup), 143 conjuntos, 167 subestações, 76% dos eventos em 240 V, ~16,4 mil eventos > 24 h, 3.955 > 48 h, ~1,4 mil > 72 h, máximo **168,8 h (7 dias)**. (Confirmado com parser sensível a aspas.)

---

## 6. Recorte explícito

- **Agente:** `SigAgente = "ELETROPAULO"` (Enel São Paulo).
- **Período:** **2023–2026** (introdução: vendaval de nov/2023 → crise da concessão → caducidade iniciada em dez/2025). *Disponibilidade:* indicadores cobrem 2020–2026; **eventos cobrem só 2025**. Nos anos sem evento, operar só com o indicador.
- **Geografia:** a pergunta é sobre o **município de São Paulo**. A concessão **não é a cidade** — os 143 conjuntos incluem a região metropolitana (ITAPECERICA DA SERRA, EMBU GUAÇU, CAUCAIA/Cotia, RIBEIRÃO PIRES, TABOÃO DA SERRA, JORDANÉSIA/Cajamar, JUQUITIBA, EMBU; RAPOSO TAVARES é ambíguo). **Filtrar a capital antes de cruzar.**

> **Obstáculo estrutural (é o coração do método):** conjunto ANEEL **≠** distrito **≠** setor censitário. Isolar a capital e cruzar com o IBGE exige um **crosswalk documentado e validado caso a caso**.

---

## 7. Entregáveis — datasets tratados (`data/processed/`)

1. **`dec_fec_anual_por_conjunto.csv`** — DEC e FEC **anuais** (soma dos 12 meses) por conjunto e por ano, filtrado à Eletropaulo; variantes relevantes (`-IP/-IN-`, `X`) ao lado.
2. **`experiencia_por_conjunto.csv`** — a partir dos eventos: nº de eventos não programados, UC total, duração mediana/p95/máxima, % de eventos ≥ 24 h, e **`DEC_reconstruido`** = `Σ(duração × UC_afetadas) / UC_total`, **`FEC_reconstruido`** = `UC_afetadas_total / UC_total`.
3. **`crosswalk_conjunto_distrito.csv`** — conjunto → distrito/setor, com nota de confiança e fonte por linha.
4. **`eventos_tratados.parquet`** (ou `.csv` — decidir pelo tamanho) — os eventos já limpos, filtrados à Eletropaulo e à capital, com `duracao_h` calculada.

---

## 8. Os gráficos (claro, objetivo, uma mensagem cada)

Cada figura abaixo sustenta um ponto da narrativa. Priorizar legibilidade; salvar em PNG (300 dpi) em `data/processed/figures/`, nomes que digam a mensagem.

| # | Figura | Mensagem que carrega | Dados | Tipo |
|---|---|---|---|---|
| G1 | **Ranking de escuridão** | "A escuridão se concentra em poucos conjuntos" | top-15 por DEC anual | barras horizontais ordenadas |
| G2 | **Distribuição de DEC entre conjuntos** | "Não é uniforme: é desigual" | DEC anual de todos os conjuntos | histograma/ECDF |
| G3 | **O hiato (H2)** | "Onde a vivência é pior do que o indicador admite" | `DEC_oficial` × `DEC_reconstruido` por conjunto | dispersão + reta y = x |
| G4 | **A cauda da experiência** | "Milhares de quedas passam de 24 h; a maior durou 7 dias" | duração de cada evento | histograma em escala log, marcas em 24/48/72 h |
| G5 | **A geografia da escuridão (H1)** | "O mapa da luz coincide com o mapa da segregação" | conjuntos da capital coloridos por DEC | mapa (coroplético/pontos) |
| G6 | **Quem sofre a escuridão (H1)** | "Mais escuro onde a renda é menor e a população é mais negra" | DEC × renda / % cor-preta de cada distrito | dispersão ou mapa bivariado |
| G7 | **O arco 2023–2026** | "O apagão de 2023 não foi acidente: revelou e piorou uma tendência" | DEC/FEC por mês/ano, Eletropaulo | séries temporais |
| G8 | **O que o recorte esconde (H2)** | "As variantes `-IP/-IN-` mostram o que a média dilui" | `DEC` × `DECINE`/`DECINC` de um conjunto-símbolo | barras comparativas |

**Figura-síntese sugerida:** um par para um conjunto-símbolo (PARELHEIROS ou JUQUITIBA) — em cima o DEC mensal oficial (linha suave, "tudo sob controle"); embaixo o *strip plot* dos eventos individuais com a cauda de 100+ h. O contraste **indicador × vivência** é o argumento, em uma imagem.

---

## 9. Base IBGE e cruzamento (para H1 / G5–G6)

Base correta = **Censo Demográfico 2022** (grão fino), não PNAD. Prioridade:
1. **Agregados por Setores Censitários (Universo)** — rendimento, cor/raça, composição domiciliar.
2. **Malha de Setores Censitários** (shapefile/geopackage) — polígono para o join espacial.
3. **Entorno dos domicílios** — iluminação pública, pavimentação, calçada (casa com "a qualidade do espaço público se deteriora", Caldeira).
4. **Agregados e malha por Distritos** (96 distritos da capital) — geografia intermediária mais realista para casar com os conjuntos.
5. **POF 2017–2018** — gasto domiciliar com energia por faixa de renda (regra dos 10%/5%).
6. Complemento: **CadÚnico / Atlas da Vulnerabilidade**.

**Caminhos de cruzamento, do melhor ao pior:**
- **(A) BDGD da Enel SP** (Base de Dados Geográfica da Distribuidora): rede georreferenciada → cada UC/evento vira ponto → entra no setor censitário por join espacial. **Melhor caminho; verificar acesso.**
- **(B) Sem BDGD:** geocodificar as **167 subestações** + crosswalk conjunto → distrito.
- **(C) Só nome de conjunto:** caro e sujeito a erro — **foi o que quebrou o mapa anterior** (Nominatim pôs "ALVARENGA" em Pindamonhangaba).

**Aviso metodológico obrigatório:** declarar o **problema das unidades de área modificáveis (MAUP)** — o resultado muda com o recorte. Numa etnografia de dados isso é **virtude**: o recorte **produz** o fenômeno e deve ser explicitado.

---

## 10. Rigor — o que NÃO fazer (erros já cometidos)

- ❌ **Geocodificar nome de conjunto** (Nominatim erra → mapa inválido).
- ❌ Tratar **média mensal como indicador anual** (é soma).
- ❌ **Misturar 2025 (cheio) com 2026 (parcial)** na mesma estatística.
- ❌ Levar o **hiato evento × indicador como medida "pura" de subnotificação** — é preciso **decompor** (o que a ANEEL conta/expurga, programadas, BT vs MT, granularidade, duplicações) antes de afirmar.
- ❌ Apresentar "média de médias" como experiência — a experiência está na **cauda longa**.

---

## 11. Ponto de partida no repo

- `src/explore.py`, `src/graficos.py` — pipeline anterior (contém os erros acima; usar como referência **negativa**).
- `src/analise_corrigida.py` — pipeline corrigido (soma anual, anos separados, encodings certos, uso dos eventos). **Base recomendada para a Fase 2/3.**
- `notebooks/start.ipynb` — leitura bruta de exemplo.
- `data/processed/` — saídas já geradas (usar como conferência, não como verdade).

---

## 12. Resumo em uma linha

Recortar a Eletropaulo à cidade de São Paulo, calcular **DEC/FEC anuais = soma dos 12 meses**, medir a **experiência por evento**, e quantificar o **hiato oficial × reconstruído** — cruzando com o Censo 2022 — em **gráficos claros** que sustentem as hipóteses da **geometria de poder** e do **silenciamento das métricas**.

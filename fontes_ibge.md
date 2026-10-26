# Fontes IBGE para o TCC — onde encontrar e o que baixar

> Guia de coleta. Ordem de prioridade pensada para o fluxo atual: **primeiro tratar/limpar e fazer os gráficos**; o QGIS vem depois, com os dados geográficos.
> Data: 25/10/2026.

---

## Regra de ouro

Existem **dois níveis** de dado do Censo 2022, e eles servem a momentos diferentes:

| Nível | Produto | Tamanho | Serve para |
|---|---|---|---|
| **Distrito** (96 na capital) | Agregados por Distrito | pequeno (poucos MB) | **os gráficos agora** — casa direto com o crosswalk conjunto→distrito |
| **Setor censitário** (~468 mil no Brasil) | Agregados por Setores + Malha | grande (centenas de MB) | o **mapa refinado**, depois, no QGIS |

**Comece pelo distrito.** É o recorte que você já consegue cruzar hoje, sem depender de geometria.

---

## 1. O que baixar AGORA (para os gráficos, sem QGIS)

### 1.1. Agregados por Distrito — Censo 2022

**Página de downloads do Censo 2022:**
`https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html?caminho=Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/`

**Navegação:** `Censos` → `Censo_Demografico_2022` → `Agregados_por_Setores_Censitarios`. Dentro dessa pasta há os arquivos por **setor** e as consolidações por **distrito, subdistrito, bairro e município** — escolha a de **distrito** (CSV ou XLSX).

**Página de resultados (para conferir versões e notas):**
`https://www.ibge.gov.br/estatisticas/sociais/trabalho/22827-censo-demografico-2022.html?edicao=41852&t=resultados`

**Alternativa pela SIDRA** (interface de tabelas, sem baixar arquivo):
`https://sidra.ibge.gov.br/pesquisa/censo-demografico/demografico-2022`
Escolha a tabela e, no seletor de território, o nível **Distrito**.

### 1.2. Quais arquivos baixar (decisão prática)

Na pasta **`Agregados_por_Distrito_csv`** há 13 arquivos. **Você precisa de 3** (5 se quiser idade e escolaridade). Mapeei cada variável no dicionário que você anexou:

| | Arquivo | O que traz | Variáveis |
|---|---|---|---|
| ✅ | `Agregados_por_distritos_basico_BR_20260520.zip` | população e domicílios totais — **os denominadores de toda taxa** | `V0001` pessoas, `V0002`/`V0003` domicílios |
| ✅ | `Agregados_por_distritos_cor_ou_raca_BR.zip` | composição racial — **o eixo central da H1** | `V01317` branca, `V01318` preta, `V01319` amarela, `V01320` parda, `V01321` indígena |
| ✅ | `Agregados_por_distritos_caracteristicas_domicilio2_BR_20250417.zip` | precariedade habitacional — **o proxy socioeconômico** | água `V00111`…`V00118`; banheiros `V00232`–`V00238`; lixo `V00397`–`V00402` |
| ⬜ | `..._demografia_BR.zip` | estrutura por idade e sexo | 36 variáveis |
| ⬜ | `..._alfabetizacao_BR.zip` | escolaridade (proxy de renda) | 362 variáveis |
| ❌ | `..._caracteristicas_domicilio1` e `..._3` | contagens e cruzamentos por nº de moradores | não vai usar |
| ❌ | `..._parentesco`, `..._obitos`, `..._indigenas`, `..._quilombolas` | fora do recorte | — |

**Os arquivos são do Brasil inteiro.** Depois de descompactar, filtre `CD_MUN = 3550308` (São Paulo) — senão vem distrito de todo o país.

### 1.3. ⚠️ Não existe renda nesses arquivos

Pesquisei o dicionário inteiro (1.411 variáveis, 8 temas): **zero ocorrências de "renda" ou "rendimento"**. O produto *Agregados por Setores Censitários — Resultados do Universo* cobre o questionário básico, e **renda só é perguntada na Amostra**. As tabelas de renda da SIDRA, por sua vez, descem até **município — não até distrito**.

Isso não trava o TCC. Três caminhos, em ordem de praticidade:

1. **Use os proxies que existem** (recomendado). Para a H1, o argumento não precisa de "renda": precisa mostrar que **escuridão, precariedade habitacional e população negra coincidem no mesmo território**. Cor/raça (`V01317`–`V01321`), saneamento e escolaridade fazem esse trabalho — e são dados oficiais, no grão do distrito.
2. **Renda por distrito de fonte secundária:** o **Mapa da Desigualdade** (Rede Nossa São Paulo / Instituto Cidades Sustentáveis) publica renda média e % de população negra para os **96 distritos** desde 2012. Confira a edição mais recente e a nota metodológica (edições antigas usavam o Censo 2010). Cite como fonte secundária, não como IBGE.
3. **Microdados da Amostra do Censo 2022:** o caminho mais rigoroso e o mais pesado — calcular a renda a partir dos microdados. Só vale se você quiser mesmo a variável renda no grão do distrito.

> **Use o dicionário de dados.** É o `dicionario_de_dados_agregados_por_setores_censitarios_*.xlsx`: aba **"Dicionário não PCT"** traz `Variável` + `Descrição` de todas as 1.411. Sem ele você não sabe o que é cada `V…`.

### 1.3. A lista oficial dos 96 distritos (para o crosswalk)

Antes de preencher o crosswalk à mão, pegue os nomes **oficiais** — evita erro de digitação e de grafia:

`https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308/distritos`

(Código `3550308` = município de São Paulo. Cole no navegador; retorna JSON com os distritos.)

Documentação: `https://servicodados.ibge.gov.br/api/docs/localidades`

---

## 2. O que baixar DEPOIS (para o QGIS)

Só quando chegar na fase do mapa.

### 2.1. Malha de Distritos — Censo 2022
Página: `https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html`
Escolha **Malha de Distritos**, UF **São Paulo**, formato **GeoPackage (.gpkg)** (melhor que shapefile: um arquivo só, aceita nomes longos).

Metadados: `https://metadadosgeo.ibge.gov.br/geonetwork_ibge/srv/api/records/2646a5cf-07b8-415d-b589-e7f770e4e857`

### 2.2. Malha de Setores Censitários — Censo 2022
Pasta direta (shapefile):
`https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/setores/shp/BR/`
Arquivo do Brasil: **`BR_setores_CD2022.zip`** (~738 MB, nov/2024).

> **Baixe por UF, não o Brasil inteiro.** Deve haver a pasta por estado (`.../shp/SP/`); o arquivo de SP é uma fração do tamanho e é tudo o que você precisa.

### 2.3. Agregados por Setor Censitário
Mesma pasta de downloads do item 1.1, mas os arquivos **por setor** (~468 mil linhas, milhares de variáveis). É grande — só baixe quando for fazer o join espacial.

---

## 3. Fontes complementares (fortalecem o argumento)

### 3.1. Entorno dos Domicílios — Censo 2022
Mede a infraestrutura **no entorno** do domicílio: iluminação pública, pavimentação, calçada, arborização, bueiro, esgoto.
`https://www.ibge.gov.br/estatisticas/sociais/habitacao/22827-censo-demografico-2022.html`
Isso conversa direto com a passagem da Caldeira sobre a deterioração do espaço público — e mostra que a precariedade não é só da rede elétrica, é do território.

### 3.2. POF 2017–2018 — gasto com energia por faixa de renda
`https://www.ibge.gov.br/estatisticas/sociais/rendimento-despesa-e-consumo/24786-pesquisa-de-orcamentos-familiares-2.html`
Não é geográfico, mas é a melhor evidência para a regra dos 10%/5% (pobreza energética). Sustenta o trecho da conta de luz asfixiando o orçamento.

### 3.3. CadÚnico / Atlas da Vulnerabilidade
Complemento não-IBGE, para cruzar pobreza extrema com o território. Útil como camada de contexto.

---

## 4. Cuidados que vão te poupar retrabalho

1. **Universo ≠ Amostra.** Confirmado no dicionário: o produto "Resultados do Universo" **não tem nenhuma variável de renda**. Renda está na **Amostra**, e as tabelas de renda da SIDRA param no **município**. Para o distrito, use os proxies do Universo ou o Mapa da Desigualdade (§1.3).
2. **Sigilo estatístico.** Setores com menos de 5 domicílios particulares permanentes têm a maioria das variáveis **omitidas** (aparecem como `x`). Isso **não é erro** — é regra do IBGE. E é, por si só, um achado para a sua tese: o dado some justamente onde a precariedade é maior.
3. **Versão vigente.** Houve correção metodológica em **abril/2025** (realocação de setores, ajuste de variáveis). Baixe a versão atual, não uma cópia antiga que circule por aí.
4. **Formato dos CSV do IBGE:** normalmente separador `;`, decimal com **vírgula**, encoding **UTF-8** (às vezes `latin-1` em produtos antigos). Trate como string na leitura e converta depois — é o mesmo cuidado que você já aplicou nos dados da ANEEL.
5. **Distrito ≠ conjunto da ANEEL.** O crosswalk continua sendo o gargalo. O Censo te dá o dado do distrito; ele não te diz a que distrito pertence o conjunto "PARELHEIROS" — isso é a sua decisão documentada (e o MAUP entra no texto do TCC).
6. **Não confunda com o produto preliminar** "Agregados por Setores Censitários preliminares: População e domicílios". É outro arquivo, com menos variáveis.

---

## 5. Como cada fonte vira gráfico

| Fonte | Variável | Gráfico |
|---|---|---|
| Agregados por distrito | % população preta + parda (`V01318`+`V01320`) | dispersão **DEC × % negro** por distrito |
| Agregados por distrito | % domicílios sem banheiro (`V00238`) | dispersão **DEC × precariedade habitacional** |
| Agregados por distrito | % domicílios sem coleta de lixo (`V00397`–`V00402`) | dispersão **DEC × saneamento** |
| Agregados por distrito | % de analfabetos (tema Alfabetização) | dispersão **DEC × escolaridade** |
| Mapa da Desigualdade (fonte secundária) | renda média por distrito | dispersão **DEC × renda** |
| Entorno dos domicílios | % com iluminação pública / pavimentação | dispersão **DEC × qualidade do entorno** |
| POF 2017–2018 | gasto com energia por faixa de renda | barras **comprometimento da renda** |
| Seu DEC/FEC (ANEEL) | DEC e FEC anuais | ranking, série 2020–2026, hiato oficial × reconstruído |

> Todos esses gráficos são de **duas variáveis** e não exigem mapa. É por isso que dá para fazê-los antes do QGIS.

---

## Ordem prática

1. Baixar **agregados por distrito** + o **dicionário**.
2. Pegar a **lista oficial dos 96 distritos** pela API.
3. Preencher o **crosswalk** (143 conjuntos → distrito / não-capital).
4. Juntar DEC/FEC + IBGE por distrito → **os gráficos**.
5. Só então: baixar **malha** e **setores** → QGIS.

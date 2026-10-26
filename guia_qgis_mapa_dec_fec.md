# Guia do zero: mapas de DEC/FEC no QGIS
### Para o TCC de energia — Eletropaulo / São Paulo (recorte 2023–2026)

> Escrito para quem **nunca mexeu com SIG**. Siga na ordem. Nada aqui assume conhecimento prévio.

---

## 0. O que você vai construir

Dois mapas, para **cada ano** do recorte (2023, 2024, 2025, 2026):

- **Mapa A — coroplético por distrito:** cada um dos **96 distritos** da capital pintado conforme o **DEC** (depois outro conforme o **FEC**).
- **Mapa B — pontos por subestação:** as **167 subestações** da Eletropaulo plotadas como pontos.

---

## 1. Instalar o QGIS — a decisão que faltava

**Instale o instalador normal, na versão LTR (Long Term Release).**

1. Vá em **qgis.org/download** e baixe o **QGIS LTR** para Windows (arquivo `.msi`).
2. Next → Next → Finish. Pronto.
3. **Cancele o OSGeo4W** (aquela tela de pacotes). Ele também instala o QGIS, mas é um gerenciador de pacotes complexo, pensado para quem precisa de várias versões ao mesmo tempo. Para você, é só risco de errar: na sua imagem **nada estava selecionado** (tudo em `Skip`) — se tivesse clicado em "Avançar", o QGIS não instalava.

O que você **NÃO** precisa: GRASS, SAGA, `qgis-server`, `qgis-dev`, `qgis-oracle-provider`, `qgis-pdb`, `qgis-grass-plugin`. Se algum tutorial mandar instalar "extras", ignore.

---

## 2. O que você precisa além do QGIS

**Nada de software.** O QGIS sozinho desenha o mapa. O que falta são **4 insumos**, e um deles é o trabalho de verdade:

| # | Insumo | Situação |
|---|---|---|
| 1 | **Malha de distritos do IBGE (Censo 2022)** | você baixa — §4 |
| 2 | **Tabela DEC/FEC tratada** | **já gerei** — `data/processed/dec_fec_anual_por_conjunto.csv` — §3 |
| 3 | **Crosswalk conjunto → distrito** | você monta — §6.1 (o trabalho real) |
| 4 | **Coordenadas das subestações** | vem da BDGD da Enel — §7 |

O motivo de ser assim: seu DEC/FEC está por **conjunto de unidades consumidoras**, e conjunto **não é uma forma no mapa** — é só um nome. Para o QGIS pintar, ele precisa de uma **camada geográfica** com uma coluna que case com a sua tabela. Reunir as duas é o insumo 3.

---

## 3. Arquivos que já preparei (na pasta `data/processed/`)

- **`dec_fec_anual_por_conjunto.csv`** — DEC e FEC **anuais** (soma dos 12 meses) por conjunto, **2020 a 2026**, só Eletropaulo. Colunas: `DscConjUndConsumidoras`, `AnoIndice`, `DEC`, `FEC`. É a sua tabela principal para o mapa.
- **`todos_indicadores_anuais_por_conjunto.csv`** — o mesmo, com **todas as variantes** (`DECINE`, `DECINC`, `FECXPC`...). Serve para o argumento do "silenciamento das métricas".
- **`lista_conjuntos_eletropaulo.csv`** — os **143 conjuntos** com suas subestações. É a lista para você montar o crosswalk (§6.1).

> Sanidade: em 2025 o maior DEC é **JUQUITIBA (32,3 h)**; depois ITAPECERICA DA SERRA (17,2), VARGEM GRANDE (15,9), PARELHEIROS (15,5). É a periferia no topo, como a hipótese prevê.

---

## 4. Baixar a malha de distritos do IBGE

Você precisa dos polígonos dos distritos. Duas opções — escolha **uma**.

**Opção A — baixar o arquivo (mais simples de entender):**
1. Vá na página **Malhas Territoriais** do IBGE: `https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html`
2. Procure **"Malha de Distritos"** (Censo 2022) → escolha a **UF: São Paulo (SP)** → baixe o **GeoPackage (`.gpkg`)** ou **Shapefile (`.zip`)**.
3. Descompacte em `data/raw/`.

**Opção B — carregar direto do servidor do IBGE (sem baixar nada):**
1. No QGIS: menu **Camada → Adicionar Camada → Adicionar Camada WFS**.
2. **Novo** → Nome: `IBGE` · URL: `https://geoservicos.ibge.gov.br/geoserver/wfs` → OK.
3. **Conectar** → na caixa de filtro digite `distrito` → selecione a camada de malha de distritos → **Adicionar**.

Depois, em qualquer opção, você vai **filtrar só a capital**: a malha de SP traz o estado inteiro; filtre `NM_MUN` = `São Paulo` (ou o campo equivalente, tipo `NM_MUNICIPIO`).

---

## 5. Ajustes iniciais no QGIS (uma vez só)

- **Idioma:** `Configurações → Opções → Geral → Locale` (ou "Português"). 
- **Sistema de referência (SRC):** `Projeto → Propriedades → SRC` → escolha **EPSG:4674 (SIRGAS 2000)**. É o sistema oficial do Brasil; deixa tudo alinhado.
- **Salvar projeto:** `Projeto → Salvar como…` → `data/processed/mapa_dec_fec.qgz`.

---

## 6. Mapa A — coroplético por distrito

### 6.1. O crosswalk (o trabalho real)

Você precisa de uma tabela que diga **a que distrito cada conjunto pertence**. Como documentos:

1. Abra `lista_conjuntos_eletropaulo.csv` no Excel/LibreOffice. Você verá os 143 conjuntos.
2. Crie duas colunas novas: **`municipio`** e **`distrito`**.
3. Para cada conjunto, preencha:
   - Se for bairro da **capital** → escreva o **distrito** (ex.: `MOOCA` → distrito *Mooca*; `JAÇANÃ` → *Jaçanã*; `IBIRAPUERA` → *Moema*).
   - Se for de **outro município** (BARUERI, OSASCO, DIADEMA, ITAPEVI, COTIA, EMBU, ITAPECERICA DA SERRA, RIBEIRÃO PIRES, TABOÃO DA SERRA, SANTO ANDRÉ, SÃO BERNARDO, MAUÁ, JANDIRA, JUQUITIBA, CARAPICUIBA…) → marque `NAO-CAPITAL` e **exclua do mapa**.
   - Se estiver em dúvida → marque `?` e confira depois.
4. Salve como **`data/processed/crosswalk_conjunto_distrito.csv`** (com as colunas `DscConjUndConsumidoras`, `municipio`, `distrito`).

> ⚠️ **Isto é para validar, não para adivinhar.** Errar aqui contamina o mapa. Vá conferindo pelo Google Maps os nomes que não tiver certeza. Alguns conjuntos têm nome de bairro que existe em mais de um município — é por isso que o campo `municipio` é obrigatório.

> ⚠️ **Cuidado de método (MAUP):** um conjunto pode cobrir mais de um distrito, e nem todo conjunto é um bairro exato. Anote no texto do TCC que o recorte **produz** o resultado — numa etnografia de dados, isso é parte do argumento, não um defeito escondido.

### 6.2. Agregar por distrito

Pegue `dec_fec_anual_por_conjunto.csv`, junte o `distrito` (via crosswalk) e calcule o DEC/FEC **por distrito**. Salve como `dec_fec_por_distrito.csv` com: `distrito`, `AnoIndice`, `DEC`, `FEC`.

> Se um distrito tiver mais de um conjunto, o correto é uma **média ponderada pelo nº de consumidores** (o DEC é "horas por unidade consumidora"). Se fizer média simples, diga no texto que foi média simples.

### 6.3. Montar no QGIS

1. **Camada → Adicionar Camada → Adicionar Camada Vetorial** → selecione a malha de distritos (`.gpkg`/`.shp`). Ela aparece no mapa.
2. Filtre a capital (botão direito na camada → **Filtrar…** → `"NM_MUN" = 'São Paulo'`).
3. **Camada → Adicionar Camada → Adicionar Camada de Texto Delimitado** → escolha `dec_fec_por_distrito.csv` → marque "Primeira linha = nomes dos campos" → **OK**.
4. **Join:** botão direito na camada de distritos → **Propriedades → Uniões (Joins)** → `+` → campo de junção: o nome do distrito (na malha) ↔ `distrito` (no CSV) → OK.
5. **Simbologia:** botão direito na camada → **Propriedades → Simbologia** → na lista suspensa escolha **Graduado (Graduated)** → Coluna: `DEC` (do join) → escolha a **rampa de cores** → **Classificar** → **OK**. O mapa pinta por DEC.
6. **Rótulos:** aba **Rótulos** → "Rótulo único" → campo do nome do distrito.
7. Repita com **FEC** (duplique a camada: botão direito → **Duplicar Camada**).

---

## 7. Mapa B — subestações (pontos)

O seu arquivo de eventos dá o **código** da subestação (ex.: `IBP`, `JAC`, `VMA`), mas **não a coordenada**. Então você precisa de um CSV de pontos: `subestacao`, `lat`, `lon`, `DEC`, `FEC`, `AnoIndice`.

**De onde vêm as coordenadas:**
- **Melhor caminho:** a **BDGD da Enel SP** (Base de Dados Geográfica da Distribuidora, que a concessionária entrega à ANEEL) — é a rede georreferenciada oficial, com subestações, alimentadores e transformadores. Verificar a forma de acesso (a ANEEL publica as BDGD).
- **Alternativa rápida (menos precisa):** os códigos são abreviações do lugar (`IBP` = Ibirapuera, `JAC` = Jaçanã, `VMA` = Vila Mariana). Dá para geocodificar o nome expandido — mas **valide cada ponto no mapa**, porque geocodificação por texto erra (foi o que jogou "ALVARENGA" em Pindamonhangaba no mapa antigo).

Depois:
1. **Adicionar Camada de Texto Delimitado** no CSV de pontos, apontando as colunas de X (`lon`) e Y (`lat`), e escolha **EPSG:4674**.
2. **Simbologia → Graduado** pela coluna `DEC`; ou **Tamanho proporcional** pelo valor.

> Se as coordenadas demorarem a sair, você pode adiantar o argumento com um **gráfico de barras (ranking das piores subestações)**, feito em Python/matplotlib — não precisa de coordenada. O mapa por pontos entra depois.

---

## 8. Repetir para cada ano (2023–2026)

Três modos, do mais simples ao mais elaborado:

- **Simples:** para cada ano, um projeto/arquivo separado. Você troca só o `AnoIndice` usado na simbologia (filtro da tabela).
- **Prático:** use a **Calculadora de Campos** ou um **filtro por `AnoIndice`** e exporte uma imagem por ano.
- **Elegante (recomendado para o TCC):** monte uma **prancha 2×2** com os quatro anos lado a lado (Layout de Impressão, §9). A leitura da **evolução** da escuridão, ano a ano, é o argumento visual.

---

## 9. Exportar a figura

1. **Projeto → Novo Layout de Impressão** → nome: `DEC_2025`.
2. **Adicionar Mapa** → desenhe o retângulo → o mapa aparece.
3. Adicione **Legenda**, **Escala** (só se necessário) e **Rótulo/Título**.
4. **Layout → Exportar como Imagem** → PNG, **300 dpi** → salve em `data/processed/figures/`.
5. Repita por ano. Para a prancha 2×2, crie 4 itens de mapa no mesmo layout.

---

## 10. Checklist final

- [ ] QGIS LTR instalado e aberto
- [ ] Malha de distritos de SP carregada e filtrada à capital
- [ ] `crosswalk_conjunto_distrito.csv` preenchido e conferido
- [ ] `dec_fec_por_distrito.csv` gerado
- [ ] Mapa A (DEC) e (FEC) pintados por distrito
- [ ] Mapa B (subestações) montado (ou o ranking em barras como plano B)
- [ ] Um mapa por ano + a prancha 2×2
- [ ] PNG 300 dpi exportado para `data/processed/figures/`

---

## 11. Links úteis

- Instalar QGIS: `https://qgis.org/download/`
- Página de Malhas Territoriais do IBGE: `https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html`
- Metadados da Malha de Distritos (Censo 2022): `https://metadadosgeo.ibge.gov.br/geonetwork_ibge/srv/api/records/2646a5cf-07b8-415d-b589-e7f770e4e857`
- Geoserviço IBGE (WFS/WMS): `https://geoservicos.ibge.gov.br/geoserver/web/`
- PRODIST Módulo 8 (regras do DEC/FEC): `https://www2.aneel.gov.br/cedoc/aren2021956_2_7.pdf`

---

> **Resumo do fluxo:** baixar a malha de distritos → montar o **crosswalk conjunto→distrito** → gerar `dec_fec_por_distrito.csv` → no QGIS, **join** + **simbologia graduada** → exportar um mapa por ano. O QGIS é a **última** etapa; o crosswalk é o que destrava tudo.

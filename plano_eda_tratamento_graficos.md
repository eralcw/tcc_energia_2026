# Plano: EDA → tratamento → gráficos

> Como eu conduziria a análise dos dados do IBGE para o desenvolvimento do TCC.
> Data: 26/10/2026.

---

## A lógica geral

O dado do IBGE não é o objeto do TCC — ele é o **contraponto socioespacial** que dá sentido ao DEC/FEC. A sequência não é burocrática: cada fase produz a informação que a seguinte consome.

```
1. EDA          → o que existe, o que falta, o que está quebrado
2. TRATAMENTO   → transforma o bruto em uma linha por distrito, pronta para juntar
3. GRÁFICOS     → cada figura responde a uma pergunta do argumento
```

**Regra:** nenhuma linha de tratamento é escrita antes do EDA. O EDA diz qual tratamento é necessário; adivinhar gera retrabalho (foi o que aconteceu no pipeline anterior da ANEEL, que tratou média como anual sem olhar a série mensal).

---

## Fase 1 — EDA (diagnóstico do bruto)

Não é "olhar os dados". É responder perguntas específicas:

**1.1. Estrutura**
- Quantas linhas e colunas? Qual o separador, o encoding, o decimal?
- Quais são as colunas de identificação (`CD_DIST`, `NM_DIST`, `CD_MUN`, `NM_MUN`)? Os nomes variam entre produtos do IBGE — não presumir.
- ⚠️ **Armadilha de nomenclatura:** o dicionário "Básico" usa 4 dígitos (`V0001` = total de pessoas) e o "Dicionário não PCT" usa 5 (`V00001` = domicílios). Confundir os dois troca o numerador pelo denominador.

**1.2. Cobertura**
- Os **96 distritos** da capital estão todos presentes? Quais faltam?
- Quantos valores ausentes por variável? No IBGE, ausência vem como **`x`** (sigilo estatístico), `-` ou vazio — não como `NaN`. **Contar `x` é parte do diagnóstico**, porque `x` marca setor com menos de 5 domicílios: o dado desaparece onde a precariedade é maior.

**1.3. Sanidade**
- A soma da população dos 96 distritos bate com a população da capital no Censo 2022 (~11,4 milhões)? Se não bater, o filtro está errado.
- Há distrito com população zero ou absurdamente alta? (sinal de mistura de municípios)
- Os percentuais calculados dão entre 0 e 100?

**1.4. Variabilidade — a pergunta que decide o TCC**
- Qual o **mínimo, mediana e máximo** de % população negra entre distritos? Se variar de 5% a 60%, há sinal. Se todos forem parecidos, a hipótese espacial não se sustenta com esse dado — e é melhor descobrir agora.
- O mesmo para saneamento e escolaridade.

**1.5. Correlações preliminares**
- Matriz de correlação entre as variáveis do IBGE. Se % negro, % sem banheiro e % sem coleta de lixo andam juntas, elas formam **um mesmo eixo de precariedade** — e isso simplifica a narrativa.

**Saída:** um notebook `notebooks/01_eda_ibge.ipynb` com essas respostas e uma lista curta de problemas a tratar.

---

## Fase 2 — Tratamento

### 2.1. Limpeza básica
1. Filtrar `CD_MUN = 3550308` (São Paulo). Os arquivos são do Brasil inteiro.
2. Converter `x`, `-`, `..` e vazio → `NaN`.
3. Decimal: vírgula → ponto; remover separador de milhar.
4. Padronizar o nome do distrito: maiúsculas, sem acento, sem espaço duplo — para o join não falhar por "Jaçanã" ≠ "JACANA".

### 2.2. Indicadores derivados (o que realmente entra no gráfico)

Nunca usar contagem bruta: usar **proporção**, sempre com denominador explícito.

| Indicador | Fórmula | Variáveis |
|---|---|---|
| % população preta + parda | (`V01318` + `V01320`) / `V0001` × 100 | cor/raça ÷ total de pessoas |
| % domicílios sem banheiro | `V00238` / `V00001` × 100 | DPPO sem banheiro ÷ DPPO total |
| % lixo em destino inadequado | (`V00401` + `V00402`) / `V00001` × 100 | lixo em terreno baldio + outro destino |
| % domicílios sem rede de água | (`V00001` − `V00111`) / `V00001` × 100 | complemento da rede geral |
| % analfabetos (15+) | do tema Alfabetização | opcional |

> **Conferir cada denominador no dicionário.** Um percentual com denominador errado é pior do que não ter o gráfico: ele parece certo e engana.

### 2.3. A ponte: crosswalk conjunto → distrito

Este é o passo que transforma dois arquivos soltos em um dataset analisável.

1. Pegar a lista oficial dos 96 distritos pela API do IBGE (ou da malha).
2. Para cada um dos 143 conjuntos da Eletropaulo, decidir: **distrito da capital** / **outro município** / **ambíguo**.
3. Nos casos de nome idêntico ao distrito (MOOCA, TUCURUVI, PINHEIROS, LAPA, ITAQUERA, GUAIANAZES, PARELHEIROS…), o casamento é direto e seguro.
4. Nos demais, **conferir caso a caso** — é aqui que o mapa antigo quebrou, ao geocodificar por texto.
5. Registrar a decisão e o grau de confiança em cada linha do crosswalk. O TCC precisa poder auditar isso.

**Decisão de ponderação:** se um distrito tiver mais de um conjunto, agregar o DEC/FEC pela **média ponderada pelo número de consumidores** — o DEC é "horas por unidade consumidora", então média simples distorce. Se usar média simples, declarar no texto.

### 2.4. Dataset final

Uma linha por distrito, com: `distrito`, `DEC_2023..2026`, `FEC_2023..2026`, `pct_negro`, `pct_sem_banheiro`, `pct_lixo_inadequado`, `populacao`. Salvar em `data/processed/distritos_sp_completo.csv`.

---

## Fase 3 — Gráficos

Regras de desenho, aplicadas a todas as figuras: **um gráfico = uma mensagem**; o **título é a mensagem** (não o nome do eixo); eixos com unidade; legível em preto e branco; extremos anotados; mesma escala entre anos quando a comparação for temporal.

| # | Figura | Pergunta que responde | Tipo |
|---|---|---|---|
| G1 | **A escuridão se concentra** | O DEC é desigual entre distritos? | barras horizontais, top 15 + os 5 melhores |
| G2 | **Onde a pele é preta, a luz falta** | DEC e composição racial coincidem? | dispersão + reta + r de Pearson e Spearman |
| G3 | **A precariedade se sobrepõe** | DEC e saneamento coincidem? | dispersão, pontos por tercil de renda (se houver) |
| G4 | **Não é a cidade inteira que sofre** | A evolução 2023–2026 é desigual? | linhas: média dos distritos do tercil superior de % negro × tercil inferior |
| G5 | **O indicador esconde** | O DEC oficial subestima a vivência? | dispersão oficial × reconstruído, reta y = x |
| G6 | **A cauda** | Qual a distribuição real da duração das quedas? | histograma log, marcas em 24/48/72 h |

### Cuidados de interpretação (para o texto, não só para o código)

- **Correlação não é causação.** Com 96 distritos e dados transversais, o resultado é **descritivo**: mostra coincidência espacial, não prova mecanismo. O mecanismo vem da etnografia e da literatura — é isso que faz o TCC ser de Ciências Sociais, e não um relatório estatístico.
- **MAUP.** O resultado muda conforme o recorte (distrito ≠ conjunto ≠ setor). Declarar isso não enfraquece o trabalho: é parte do argumento sobre como o recorte produz o fenômeno.
- **A ausência também é dado.** Se algum distrito periférico tiver `x` em várias variáveis, isso entra na narrativa do silenciamento — não no lixo.

---

## O que eu preciso para executar

1. Os 3 zips descompactados (ou os zips) em **`data/raw/ibge/`** dentro do repo:
   - `Agregados_por_distritos_basico_BR_20260520.zip`
   - `Agregados_por_distritos_cor_ou_raca_BR.zip`
   - `Agregados_por_distritos_caracteristicas_domicilio2_BR_20250417.zip`
2. Nada mais. O dicionário já está comigo.

Com os arquivos no lugar, eu rodo o EDA primeiro — e só depois escrevo o tratamento, porque é o EDA que diz quais colunas existem de verdade.

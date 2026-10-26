"""Análise corrigida dos dados ANEEL para o TCC (Eletropaulo / São Paulo).

Correções em relação ao pipeline anterior (explore.py):
  1. DEC/FEC: os valores mensais do indicador são INCREMENTOS do mês, logo o
     indicador ANUAL = SOMA dos meses (não a média). Antes a média mensal era
     tratada como se fosse o valor do ano.
  2. Não misturar anos: separar "2025" (12 meses) de "2026" (parcial).
  3. Encoding: interrupções = latin-1; indicadores = utf-8-sig.
  4. Usar o arquivo de INTERRUPÇÕES (nível de evento) para medir a
     "experiência" (duração real de cada queda), e não só o indicador agregado.
  5. Não geocodificar nome de conjunto (Nominatim erra: "ALVARENGA" cai em
     Pindamonhangaba). Usar um crosswalk conjunto -> distrito/setor.

Uso:
    python src/analise_corrigida.py \
        --indicadores "C:/caminho/indicadores-continuidade-coletivos-2020-2029.csv" \
        --interrupcoes "C:/caminho/interrupcoes-energia-eletrica-2025.csv" \
        --ano 2025 --agente ELETROPAULO \
        --out data/processed
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

AGENTE = "ELETROPAULO"

COLUNAS_INTERRUPCOES = [
    "DatGeracaoConjuntoDados", "IdeConjuntoUnidadeConsumidora",
    "DscConjuntoUnidadeConsumidora", "DscAlimentadorSubestacao",
    "DscSubestacaoDistribuicao", "NumOrdemInterrupcao", "DscTipoInterrupcao",
    "IdeMotivoInterrupcao", "DatInicioInterrupcao", "DatFimInterrupcao",
    "DscFatoGeradorInterrupcao", "NumNivelTensao", "NumUnidadeConsumidora",
    "NumConsumidorConjunto", "NumAno", "NomAgenteRegulado", "SigAgente",
    "NumCPFCNPJ",
]


def carregar_indicadores(caminho: Path, agente: str, ano: int) -> pd.DataFrame:
    """Lê o CSV de indicadores coletivos e devolve DEC/FEC ANUAIS por conjunto.

    O valor anual é a SOMA dos 12 valores mensais (NumPeriodoIndice 1..12).
    """
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    for c in ["SigAgente", "DscConjUndConsumidoras", "SigIndicador"]:
        df[c] = df[c].astype(str).str.strip()

    # "1.234,56" -> 1234.56
    df["v"] = (
        df["VlrIndiceEnviado"].str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False).astype(float)
    )

    rec = df[
        df["SigAgente"].eq(agente)
        & df["AnoIndice"].eq(str(ano))
        & df["SigIndicador"].isin(["DEC", "FEC"])
    ]
    anual = (
        rec.groupby(["DscConjUndConsumidoras", "SigIndicador"])["v"]
        .sum()
        .unstack()
    )
    anual.columns = [f"{c}_oficial_{ano}" for c in anual.columns]
    anual.index.name = "DscConjUndConsumidoras"
    return anual


def carregar_eventos(caminho: Path, agente: str) -> pd.DataFrame:
    """Lê o CSV gigante de interrupções (latin-1, aspas com ';' embutido)."""
    partes = []
    for chunk in pd.read_csv(
        caminho, sep=";", encoding="latin-1", dtype=str, quotechar='"',
        header=None, names=COLUNAS_INTERRUPCOES, skiprows=1,
        chunksize=500_000,
    ):
        partes.append(chunk[chunk["SigAgente"].str.strip().eq(agente)])
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(
        columns=COLUNAS_INTERRUPCOES
    )
    return df


def metricas_experiencia(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Métricas por conjunto a partir dos EVENTOS (a experiência vivida)."""
    df = df.copy()
    df["conj"] = df["DscConjuntoUnidadeConsumidora"].str.strip()
    df["dur_h"] = (
        pd.to_datetime(df["DatFimInterrupcao"], errors="coerce")
        - pd.to_datetime(df["DatInicioInterrupcao"], errors="coerce")
    ).dt.total_seconds() / 3600.0
    df["uc"] = pd.to_numeric(df["NumUnidadeConsumidora"], errors="coerce")
    df["uc_total"] = pd.to_numeric(df["NumConsumidorConjunto"], errors="coerce")
    df["prog"] = df["DscTipoInterrupcao"].str.strip().eq("Programada")
    df = df[(df["dur_h"] >= 0) & (df["NumAno"] == str(ano))]
    np_ = df[~df["prog"]]

    g = np_.groupby("conj")
    exp = pd.DataFrame({
        "ide_conjunto": g["IdeConjuntoUnidadeConsumidora"].first(),
        "n_eventos_nao_prog": g.size(),
        "UC_total": g["uc_total"].max(),
        "dur_mediana_h": g["dur_h"].median().round(2),
        "dur_p95_h": g["dur_h"].quantile(0.95).round(1),
        "dur_max_h": g["dur_h"].max().round(1),
        "pct_eventos_24h": g["dur_h"].apply(lambda s: round(100 * (s >= 24).mean(), 1)),
        "UC_afetadas_soma": g["uc"].sum(),
    })
    horas_uc = g.apply(lambda x: (x["dur_h"] * x["uc"]).sum(), include_groups=False)
    exp["DEC_reconstruido"] = (horas_uc / exp["UC_total"]).round(1)
    exp["FEC_reconstruido"] = (exp["UC_afetadas_soma"] / exp["UC_total"]).round(2)
    exp.index.name = "DscConjUndConsumidoras"
    return exp


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indicadores", required=True, type=Path)
    ap.add_argument("--interrupcoes", required=True, type=Path)
    ap.add_argument("--agente", default=AGENTE)
    ap.add_argument("--ano", default=2025, type=int)
    ap.add_argument("--out", default=Path("data/processed"), type=Path)
    args = ap.parse_args()

    print("Lendo indicadores (DEC/FEC oficiais)...")
    oficial = carregar_indicadores(args.indicadores, args.agente, args.ano)

    print("Lendo eventos de interrupção (pode demorar)...")
    eventos = carregar_eventos(args.interrupcoes, args.agente)
    print(f"  {len(eventos):,} eventos de {args.agente}")

    exp = metricas_experiencia(eventos, args.ano)

    tabela = exp.join(oficial, how="left").reset_index()
    tabela = tabela.sort_values("DEC_reconstruido", ascending=False)

    args.out.mkdir(parents=True, exist_ok=True)
    destino = args.out / f"{args.agente.lower()}_{args.ano}_conjunto_corrigido.csv"
    tabela.round(2).to_csv(destino, index=False)
    print(f"\nSalvo: {destino}  ({len(tabela)} conjuntos)")

    print("\n--- Resumo ---")
    print(f"DEC oficial  (mediana): {tabela[f'DEC_oficial_{args.ano}'].median():.1f} h/ano")
    print(f"DEC eventos  (mediana): {tabela['DEC_reconstruido'].median():.1f} h/ano")
    print(f"FEC oficial  (mediana): {tabela[f'FEC_oficial_{args.ano}'].median():.1f}/ano")
    print(f"FEC eventos  (mediana): {tabela['FEC_reconstruido'].median():.1f}/ano")


if __name__ == "__main__":
    main()

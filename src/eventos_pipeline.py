"""Pipeline dos eventos de interrupção (ANEEL) — a experiência medida por queda.

Lê o CSV nacional de interrupções (2,9 GB, latin-1, separador ';' e ';' dentro
das aspas), filtra a Eletropaulo, remove duplicatas e calcula a duração de cada
evento.

Uso:
    python src/eventos_pipeline.py --eventos data/raw/interrupcoes-energia-eletrica-2025.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"

COLUNAS = [
    "DatGeracaoConjuntoDados", "IdeConjuntoUnidadeConsumidora",
    "DscConjuntoUnidadeConsumidora", "DscAlimentadorSubestacao",
    "DscSubestacaoDistribuicao", "NumOrdemInterrupcao", "DscTipoInterrupcao",
    "IdeMotivoInterrupcao", "DatInicioInterrupcao", "DatFimInterrupcao",
    "DscFatoGeradorInterrupcao", "NumNivelTensao", "NumUnidadeConsumidora",
    "NumConsumidorConjunto", "NumAno", "NomAgenteRegulado", "SigAgente",
    "NumCPFCNPJ",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eventos", type=Path,
                    default=RAIZ / "data" / "raw" / "interrupcoes-energia-eletrica-2025.csv")
    ap.add_argument("--agente", default="ELETROPAULO")
    args = ap.parse_args()

    partes = []
    for chunk in pd.read_csv(args.eventos, sep=";", encoding="latin-1", dtype=str,
                             quotechar='"', header=None, names=COLUNAS,
                             skiprows=1, chunksize=500_000):
        partes.append(chunk[chunk["SigAgente"].str.strip().eq(args.agente)])
    df = pd.concat(partes, ignore_index=True)
    print(f"eventos brutos: {len(df):,}")

    df = df.drop_duplicates(subset=["IdeConjuntoUnidadeConsumidora", "NumOrdemInterrupcao",
                                    "DatInicioInterrupcao", "DatFimInterrupcao"])
    print(f"após deduplicação: {len(df):,}")

    df["duracao_h"] = (
        pd.to_datetime(df["DatFimInterrupcao"], errors="coerce")
        - pd.to_datetime(df["DatInicioInterrupcao"], errors="coerce")
    ).dt.total_seconds() / 3600
    df = df[(df["duracao_h"] >= 0) & df["duracao_h"].notna()]

    saida = pd.DataFrame({
        "conjunto": df["DscConjuntoUnidadeConsumidora"].str.strip(),
        "subestacao": df["DscSubestacaoDistribuicao"].str.strip(),
        "tipo": df["DscTipoInterrupcao"].str.strip(),
        "inicio": df["DatInicioInterrupcao"],
        "duracao_h": df["duracao_h"].round(3),
        "uc_afetadas": pd.to_numeric(df["NumUnidadeConsumidora"], errors="coerce"),
        "tensao_v": pd.to_numeric(df["NumNivelTensao"], errors="coerce"),
    })
    saida.to_csv(PROC / "eventos_eletropaulo_2025.csv", index=False, encoding="utf-8-sig")

    print(f"salvo: {PROC / 'eventos_eletropaulo_2025.csv'}")
    print(f"duração mediana: {saida.duracao_h.median():.2f} h | p95 {saida.duracao_h.quantile(.95):.1f} h | máx {saida.duracao_h.max():.1f} h")
    print(f"eventos > 24 h: {(saida.duracao_h >= 24).sum():,} | > 48 h: {(saida.duracao_h >= 48).sum():,} | > 72 h: {(saida.duracao_h >= 72).sum():,}")


if __name__ == "__main__":
    main()

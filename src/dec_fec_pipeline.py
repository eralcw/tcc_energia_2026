"""Pipeline DEC/FEC — indicadores coletivos de continuidade (ANEEL).

Lê data/processed/dec_fec_anual_por_conjunto.csv (gerado a partir do arquivo
bruto da ANEEL) e produz o painel tratado conjunto x ano.

Decisões de tratamento (documentadas para o TCC):
  - O indicador ANUAL é a SOMA dos 12 valores mensais (os mensais são incrementos).
  - 2026 tem apenas 5 meses -> marcado como parcial e excluído de séries anuais.
  - BANDEIRANTES (2020-2023) e NOVO BANDEIRANTES (2024-2026) são o mesmo
    conjunto renomeado -> unificados.
  - Recorte geográfico: lista conservadora de conjuntos que são claramente de
    outros municípios da concessão. O restante é tratado como capital (a
    confirmar no crosswalk definitivo).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"

# Conjuntos que claramente NÃO são da capital (municípios da região metropolitana)
FORA_DA_CAPITAL = {
    "ALPHAVILLE", "BARUERI", "CARAPICUIBA", "CAUCAIA", "COTIA", "DIADEMA",
    "EMBU", "EMBU GUAÇU", "GRANJA VIANA", "ITAPECERICA DA SERRA", "ITAPEVI",
    "JANDIRA", "JORDANÉSIA", "JUQUITIBA", "MAUÁ", "OSASCO", "PARNAÍBA",
    "RIBEIRÃO PIRES", "SANTO ANDRÉ", "SÃO BERNARDO DO CAMPO", "TABOÃO DA SERRA",
}

RENOMEADOS = {"BANDEIRANTES": "NOVO BANDEIRANTES"}
ANO_PARCIAL = 2026


def main() -> None:
    d = pd.read_csv(PROC / "dec_fec_anual_por_conjunto.csv", encoding="utf-8-sig")
    d["DscConjUndConsumidoras"] = (
        d["DscConjUndConsumidoras"].astype(str).str.strip().replace(RENOMEADOS)
    )
    d["AnoIndice"] = d["AnoIndice"].astype(int)
    # recorte do TCC: 2023-2026 (o vendaval de nov/2023 abre a série)
    d = d[d["AnoIndice"].between(2023, 2026)].copy()
    d["parcial"] = d["AnoIndice"].eq(ANO_PARCIAL)
    d["municipio"] = d["DscConjUndConsumidoras"].apply(
        lambda n: "fora_da_capital" if n in FORA_DA_CAPITAL else "capital"
    )

    # um conjunto renomeado pode gerar duas linhas no mesmo ano -> consolidar
    painel = (
        d.groupby(["DscConjUndConsumidoras", "AnoIndice", "municipio"], as_index=False)
        .agg(DEC=("DEC", "sum"), FEC=("FEC", "sum"), parcial=("parcial", "max"))
        .sort_values(["DscConjUndConsumidoras", "AnoIndice"])
    )
    painel.to_csv(PROC / "dec_fec_tratado.csv", index=False, encoding="utf-8-sig")

    print(f"Painel: {len(painel)} linhas | {painel.DscConjUndConsumidoras.nunique()} conjuntos")
    print(painel.groupby("municipio").DscConjUndConsumidoras.nunique().to_string())
    print("\nDEC por ano (capitais, anos completos):")
    cap = painel[(painel.municipio == "capital") & (~painel.parcial)]
    for ano, g in cap.groupby("AnoIndice"):
        print(f"  {ano}: mediana {g.DEC.median():5.2f} h | p90 {g.DEC.quantile(.9):6.2f} h | máx {g.DEC.max():6.2f} h")

    print("\nTop 10 DEC 2025 (capital):")
    t = cap[cap.AnoIndice == 2025].nlargest(10, "DEC")
    print(t[["DscConjUndConsumidoras", "DEC", "FEC"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()

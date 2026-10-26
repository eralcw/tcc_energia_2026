"""Pipeline IBGE — Censo 2022, agregados por distrito (Universo).

Lê os três arquivos baixados em data/raw/ibge/, filtra a capital de São Paulo
(CD_MUN = 3550308) e produz uma linha por distrito com os indicadores usados
no TCC.

Decisões de tratamento (documentadas para o TCC):
  - Encoding latin-1 (ISO-8859-1), separador ';', decimal com vírgula.
  - 'basico' usa v0001..v0009 em minúsculo; os demais usam V0001.. maiúsculo.
  - Denominador dos indicadores de domicílio = soma do próprio bloco de
    categorias (equivale aos DPPO com declaração; o V00001 explícito está no
    arquivo caracteristicas_domicilio1, que não foi baixado).
  - 'x' (sigilo estatístico) -> NaN.

Uso:
    python src/ibge_pipeline.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw" / "ibge"
OUT = RAIZ / "data" / "processed"

CD_MUN_SP = "3550308"

ARQ = {
    "basico": RAW / "Agregados_por_distritos_basico_BR_20260520" / "Agregados_por_distritos_basico_BR.csv",
    "cor": RAW / "Agregados_por_distritos_cor_ou_raca_BR" / "Agregados_por_distritos_cor_ou_raca_BR.csv",
    "dom": RAW / "Agregados_por_distritos_caracteristicas_domicilio2_BR_20250417" / "Agregados_por_distritos_caracteristicas_domicilio2_BR.csv",
}

# Blocos de categorias mutuamente exclusivas (somam o total de DPPO)
BLOCO_AGUA = ["V00111", "V00112", "V00113", "V00114", "V00115", "V00116", "V00117", "V00118"]
BLOCO_BANHEIRO = ["V00232", "V00233", "V00234", "V00235", "V00236", "V00237", "V00238"]
BLOCO_LIXO = ["V00397", "V00398", "V00399", "V00400", "V00401", "V00402"]

CORES = ["V01317", "V01318", "V01319", "V01320", "V01321"]  # branca, preta, amarela, parda, indígena


def ler(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, sep=";", encoding="latin-1", dtype=str)


def num(serie: pd.Series) -> pd.Series:
    """Converte texto do IBGE em número: vírgula decimal, 'x' -> NaN."""
    s = (
        serie.astype(str)
        .str.strip()
        .replace({"x": None, "X": None, "-": None, "..": None, "": None})
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(s, errors="coerce")


def main() -> None:
    bas, cor, dom = ler(ARQ["basico"]), ler(ARQ["cor"]), ler(ARQ["dom"])

    # --- recorte: capital de São Paulo -------------------------------------
    cap = bas[bas["CD_MUN"] == CD_MUN_SP].copy()
    dist = pd.DataFrame({
        "CD_DIST": cap["CD_DIST"].values,
        "distrito": cap["NM_DIST"].values,
        "populacao": num(cap["v0001"]).values,
        "area_km2": num(cap["AREA_KM2"]).values,
    })
    dist["densidade"] = dist["populacao"] / dist["area_km2"]

    # --- cor/raça ----------------------------------------------------------
    c = cor.drop(columns=["NM_DIST"]).merge(dist[["CD_DIST"]], on="CD_DIST")
    c["pop_com_cor"] = sum(num(c[v]) for v in CORES)
    c["pct_negro"] = 100 * (num(c["V01318"]) + num(c["V01320"])) / c["pop_com_cor"]

    # --- domicílios: água, banheiro, lixo ----------------------------------
    d = dom.drop(columns=["NM_DIST"]).merge(dist[["CD_DIST"]], on="CD_DIST")
    d["base_agua"] = sum(num(d[v]) for v in BLOCO_AGUA)
    d["base_banheiro"] = sum(num(d[v]) for v in BLOCO_BANHEIRO)
    d["base_lixo"] = sum(num(d[v]) for v in BLOCO_LIXO)

    d["pct_sem_rede_agua"] = 100 * (d["base_agua"] - num(d["V00111"])) / d["base_agua"]
    d["pct_sem_banheiro"] = 100 * num(d["V00238"]) / d["base_banheiro"]
    # sem coleta = queimado (V00399) + enterrado (V00400) + terreno baldio (V00401) + outro (V00402)
    d["pct_lixo_sem_coleta"] = 100 * (
        num(d["V00399"]) + num(d["V00400"]) + num(d["V00401"]) + num(d["V00402"])
    ) / d["base_lixo"]

    # --- montagem final ----------------------------------------------------
    final = (
        dist.merge(c[["CD_DIST", "pct_negro"]], on="CD_DIST")
        .merge(d[["CD_DIST", "pct_sem_rede_agua", "pct_sem_banheiro", "pct_lixo_sem_coleta"]], on="CD_DIST")
        .sort_values("pct_negro", ascending=False)
        .reset_index(drop=True)
    )

    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / "ibge_distritos_sp.csv"
    final.round(3).to_csv(destino, index=False, encoding="utf-8-sig")

    # --- relatório ---------------------------------------------------------
    print(f"Distritos: {len(final)}")
    print(f"População somada: {final.populacao.sum():,.0f}")
    print(f"Salvo: {destino}")
    print("\nDistribuição dos indicadores:")
    for col, rot in [
        ("pct_negro", "% negro"),
        ("pct_sem_rede_agua", "% sem rede de água"),
        ("pct_sem_banheiro", "% sem banheiro"),
        ("pct_lixo_sem_coleta", "% lixo sem coleta"),
    ]:
        s = final[col]
        print(f"  {rot:<22} min {s.min():6.2f} | mediana {s.median():6.2f} | max {s.max():6.2f}")
    print("\nCorrelação (Spearman) com % negro:")
    cols = ["pct_negro", "pct_sem_rede_agua", "pct_sem_banheiro", "pct_lixo_sem_coleta", "populacao"]
    print(final[cols].corr(method="spearman")["pct_negro"].round(2).to_string())


if __name__ == "__main__":
    main()

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from branca.colormap import linear
from shapely.geometry import Point


CSV_PATH = Path("data/raw/indicadores-continuidade-coletivos-2020-2029.csv")
OUTPUT_DIR = Path("data/processed")
FIGURES_DIR = OUTPUT_DIR / "figures"
GEO_CACHE_PATH = OUTPUT_DIR / "geocoding_sp_cache.csv"

AGENTE_ALVO = "ELETROPAULO"
ANOS_RECORTE = {2025, 2026}
INDICADORES_CHAVE = {"DEC", "FEC"}
TOP_N_DESTAQUES = 10
TOP_N_MAPA = 20

sns.set_theme(style="whitegrid", context="talk")

CORES = {
    "DEC": "#8E1F2F",
    "FEC": "#1F5C87",
    "positivo": "#C0392B",
    "negativo": "#2E86C1",
    "fundo": "#F7F4EF",
    "texto": "#1F2933",
}


def carregar_dados_csv(caminho: Path) -> pd.DataFrame:
    """Lê o CSV bruto com fallback de encoding."""
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(caminho, sep=";", encoding=encoding, dtype=str)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "read_csv",
        b"",
        0,
        1,
        "Nao foi possivel ler o arquivo com utf-8-sig, utf-8 ou latin1.",
    )


def preparar_base(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza colunas e tipos para analise."""
    base = df.copy()
    base.columns = base.columns.str.strip()

    for coluna in ["SigAgente", "SigIndicador", "DscConjUndConsumidoras"]:
        base[coluna] = base[coluna].astype(str).str.strip()

    base["AnoIndice"] = pd.to_numeric(base["AnoIndice"], errors="coerce").astype("Int64")
    base["NumPeriodoIndice"] = pd.to_numeric(base["NumPeriodoIndice"], errors="coerce").astype("Int64")
    base["VlrIndiceEnviado"] = (
        base["VlrIndiceEnviado"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    base["VlrIndiceEnviado"] = pd.to_numeric(base["VlrIndiceEnviado"], errors="coerce")

    base["periodo_ref"] = (
        base["AnoIndice"].astype(str)
        + "-"
        + base["NumPeriodoIndice"].astype("Int64").astype(str).str.zfill(2)
    )

    return base


def filtrar_recorte(base: pd.DataFrame) -> pd.DataFrame:
    """Recorta ELETROPAULO para os anos 2025 e 2026."""
    return base[
        base["SigAgente"].eq(AGENTE_ALVO)
        & base["AnoIndice"].isin(ANOS_RECORTE)
        & base["SigIndicador"].isin(INDICADORES_CHAVE)
    ].copy()


def resumo_qualidade_dados(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "coluna": df.columns,
            "nulos": [df[c].isna().sum() for c in df.columns],
            "n_unicos": [df[c].nunique(dropna=True) for c in df.columns],
        }
    ).sort_values("nulos", ascending=False)


def describe_por_conjunto(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo estilo describe, separado por DscConjUndConsumidoras e indicador."""
    base = df[df["SigIndicador"].isin(INDICADORES_CHAVE)].copy()
    return (
        base.groupby(["DscConjUndConsumidoras", "SigIndicador"], as_index=False)
        .agg(
            ide_conjunto=("IdeConjUndConsumidoras", "first"),
            sig_agente=("SigAgente", "first"),
            media=("VlrIndiceEnviado", "mean"),
            mediana=("VlrIndiceEnviado", "median"),
            desvio_padrao=("VlrIndiceEnviado", "std"),
            minimo=("VlrIndiceEnviado", "min"),
            p25=("VlrIndiceEnviado", lambda s: s.quantile(0.25)),
            p75=("VlrIndiceEnviado", lambda s: s.quantile(0.75)),
            p90=("VlrIndiceEnviado", lambda s: s.quantile(0.90)),
            maximo=("VlrIndiceEnviado", "max"),
            registros=("VlrIndiceEnviado", "size"),
        )
        .sort_values(["DscConjUndConsumidoras", "SigIndicador"])
    )


def resumo_por_territorio(describe_conjuntos: pd.DataFrame) -> pd.DataFrame:
    """Junta DEC e FEC em uma linha por território para os gráficos comparativos."""
    pivot = describe_conjuntos.pivot_table(
        index=["DscConjUndConsumidoras", "ide_conjunto", "sig_agente"],
        columns="SigIndicador",
        values=["media", "mediana", "desvio_padrao", "minimo", "p25", "p75", "p90", "maximo", "registros"],
        aggfunc="first",
    ).sort_index(axis=1)
    pivot.columns = [f"{metrico.lower()}_{indicador.lower()}" for metrico, indicador in pivot.columns]
    territorios = pivot.reset_index()
    if {"media_dec", "media_fec"}.issubset(territorios.columns):
        territorios["score_vulnerabilidade"] = territorios["media_dec"] + territorios["media_fec"]
    return territorios


def _formatar_e_salvar(fig: plt.Figure, caminho: Path) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.patch.set_facecolor(CORES["fundo"])
    fig.savefig(caminho, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return caminho


def gerar_scatter_matriz_vulnerabilidade(territorios: pd.DataFrame) -> Path:
    df = territorios.dropna(subset=["media_dec", "media_fec"]).copy()
    media_dec_sp = df["media_dec"].mean()
    media_fec_sp = df["media_fec"].mean()

    df["quadrante"] = np.select(
        [
            (df["media_fec"] < media_fec_sp) & (df["media_dec"] < media_dec_sp),
            (df["media_fec"] >= media_fec_sp) & (df["media_dec"] < media_dec_sp),
            (df["media_fec"] < media_fec_sp) & (df["media_dec"] >= media_dec_sp),
        ],
        ["Baixa baixa", "Alta FEC", "Alta DEC"],
        default="Alta ambos",
    )

    cores_quadrante = {
        "Baixa baixa": "#A6D8D4",
        "Alta FEC": "#6FA8DC",
        "Alta DEC": "#E67E73",
        "Alta ambos": "#7F1D1D",
    }

    destaque = df.nlargest(12, "score_vulnerabilidade")
    fig, ax = plt.subplots(figsize=(14, 11), constrained_layout=True)
    fig.patch.set_facecolor(CORES["fundo"])

    for quadrante, grupo in df.groupby("quadrante"):
        ax.scatter(
            grupo["media_fec"],
            grupo["media_dec"],
            s=140,
            alpha=0.85,
            color=cores_quadrante[quadrante],
            edgecolor="white",
            linewidth=0.8,
            label=quadrante,
        )

    for _, linha in destaque.iterrows():
        ax.annotate(
            linha["DscConjUndConsumidoras"],
            (linha["media_fec"], linha["media_dec"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
            color=CORES["texto"],
        )

    ax.axvline(media_fec_sp, color=CORES["negativo"], linestyle="--", linewidth=1.5, alpha=0.8)
    ax.axhline(media_dec_sp, color=CORES["positivo"], linestyle="--", linewidth=1.5, alpha=0.8)
    ax.text(media_fec_sp, ax.get_ylim()[1], "  média FEC SP", color=CORES["negativo"], va="top", fontsize=11)
    ax.text(ax.get_xlim()[1], media_dec_sp, "média DEC SP  ", color=CORES["positivo"], ha="right", va="bottom", fontsize=11)

    ax.set_xlabel("Média FEC", fontsize=13)
    ax.set_ylabel("Média DEC", fontsize=13)
    ax.set_title("Matriz de vulnerabilidade: DEC x FEC por conjunto", fontsize=15, fontweight="bold")
    ax.legend(title="Quadrantes", frameon=True, loc="upper left")
    ax.grid(True, alpha=0.18)

    return _formatar_e_salvar(fig, FIGURES_DIR / "01_scatter_matriz_vulnerabilidade.png")


def _boxplot_stats(df: pd.DataFrame, indicador: str, top_n: int = TOP_N_DESTAQUES) -> list[dict[str, float | str]]:
    subset = df[df["SigIndicador"].eq(indicador)].copy().sort_values("media", ascending=False).head(top_n)
    stats: list[dict[str, float | str]] = []
    for _, row in subset.iterrows():
        stats.append(
            {
                "label": row["DscConjUndConsumidoras"],
                "whislo": float(row["minimo"]),
                "q1": float(row["p25"]),
                "med": float(row["mediana"]),
                "q3": float(row["p75"]),
                "whishi": float(row["maximo"]),
                "mean": float(row["media"]),
                "fliers": [],
            }
        )
    return stats


def gerar_boxplots_customizados(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(nrows=2, figsize=(16, 15), constrained_layout=True)
    fig.suptitle(
        "Anatomia da desigualdade: distribuição mensal dos 10 territórios mais críticos",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador, cor in zip(axes, ["DEC", "FEC"], [CORES["DEC"], CORES["FEC"]]):
        stats = _boxplot_stats(describe_conjuntos, indicador)
        box = ax.bxp(
            stats,
            orientation="horizontal",
            showmeans=True,
            meanline=True,
            patch_artist=True,
            showfliers=False,
            widths=0.7,
        )
        for patch in box["boxes"]:
            patch.set_facecolor(cor)
            patch.set_alpha(0.55)
            patch.set_edgecolor(CORES["texto"])
        for median in box["medians"]:
            median.set_color("#111111")
            median.set_linewidth(2.2)
        for mean in box["means"]:
            mean.set_color("#111111")
            mean.set_linewidth(1.8)
        for whisker in box["whiskers"]:
            whisker.set_color(CORES["texto"])
            whisker.set_linewidth(1.2)
        for cap in box["caps"]:
            cap.set_color(CORES["texto"])
            cap.set_linewidth(1.2)

        ax.set_title(f"{indicador}: mínimo, quartis, mediana e máximo", fontsize=14, fontweight="bold")
        ax.set_xlabel("Índice")
        ax.set_ylabel("Conjunto consumidor")
        ax.grid(True, axis="x", alpha=0.2)

    return _formatar_e_salvar(fig, FIGURES_DIR / "02_boxplot_customizado.png")


def gerar_barras_divergentes(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(nrows=2, figsize=(16, 15), constrained_layout=True)
    fig.suptitle(
        "Cabo de guerra urbano: desvios em relação à média de São Paulo",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador in zip(axes, ["DEC", "FEC"]):
        subset = describe_conjuntos[describe_conjuntos["SigIndicador"].eq(indicador)].copy()
        media_sp = subset["media"].mean()
        subset["delta"] = subset["media"] - media_sp
        subset = pd.concat(
            [subset.nsmallest(10, "delta"), subset.nlargest(10, "delta")],
            ignore_index=True,
        ).drop_duplicates(subset=["DscConjUndConsumidoras"])
        subset = subset.sort_values("delta")

        colors = [CORES["negativo"] if valor < 0 else CORES["positivo"] for valor in subset["delta"]]
        ax.barh(subset["DscConjUndConsumidoras"], subset["delta"], color=colors, alpha=0.92)
        ax.axvline(0, color=CORES["texto"], linewidth=1.2)
        ax.set_title(f"{indicador} - diferença em relação à média de SP ({media_sp:.3f})", fontsize=14, fontweight="bold")
        ax.set_xlabel("Diferença da média territorial para a média geral")
        ax.set_ylabel("")
        ax.grid(True, axis="x", alpha=0.2)

        for y, valor in enumerate(subset["delta"]):
            alinhamento = "left" if valor >= 0 else "right"
            deslocamento = 0.02 if valor >= 0 else -0.02
            ax.text(valor + deslocamento, y, f"{valor:+.2f}", va="center", ha=alinhamento, fontsize=9)

    return _formatar_e_salvar(fig, FIGURES_DIR / "03_barras_divergentes.png")


def gerar_error_bars(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(nrows=2, figsize=(16, 15), constrained_layout=True)
    fig.suptitle(
        "Incerteza territorial: média e desvio-padrão dos 10 territórios mais críticos",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador, cor in zip(axes, ["DEC", "FEC"], [CORES["DEC"], CORES["FEC"]]):
        subset = describe_conjuntos[describe_conjuntos["SigIndicador"].eq(indicador)].copy().nlargest(TOP_N_DESTAQUES, "media")
        subset = subset.sort_values("media")
        ax.barh(
            subset["DscConjUndConsumidoras"],
            subset["media"],
            xerr=subset["desvio_padrao"],
            color=cor,
            alpha=0.82,
            capsize=4,
            edgecolor="white",
            linewidth=0.8,
        )
        ax.set_title(f"{indicador} - média com desvio padrão", fontsize=14, fontweight="bold")
        ax.set_xlabel("Índice")
        ax.set_ylabel("")
        ax.grid(True, axis="x", alpha=0.2)

        for y, (_, row) in enumerate(subset.iterrows()):
            ax.text(row["media"] + row["desvio_padrao"] + 0.02, y, f"{row['media']:.2f} ± {row['desvio_padrao']:.2f}", va="center", fontsize=9)

    return _formatar_e_salvar(fig, FIGURES_DIR / "04_error_bars.png")


def geocodificar_territorio(territorio: str) -> dict[str, float | str] | None:
    consulta = f"{territorio}, Sao Paulo, SP, Brasil"
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "tcc-energia-2026/1.0"}
    resposta = requests.get(url, params={"q": consulta, "format": "jsonv2", "limit": 1}, headers=headers, timeout=20)
    resposta.raise_for_status()
    dados = resposta.json()
    if not dados:
        return None
    item = dados[0]
    return {
        "DscConjUndConsumidoras": territorio,
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "display_name": item.get("display_name", consulta),
        "query": consulta,
    }


def carregar_ou_geocodificar(territorios: pd.DataFrame) -> pd.DataFrame:
    if GEO_CACHE_PATH.exists():
        cache = pd.read_csv(GEO_CACHE_PATH)
    else:
        cache = pd.DataFrame(columns=["DscConjUndConsumidoras", "lat", "lon", "display_name", "query"])

    cache_nomes = set(cache.get("DscConjUndConsumidoras", pd.Series(dtype=str)).astype(str).tolist())
    territorios_faltantes = [valor for valor in territorios["DscConjUndConsumidoras"].dropna().drop_duplicates().tolist() if valor not in cache_nomes]

    novos_registros = []
    for territorio in territorios_faltantes[:TOP_N_MAPA]:
        try:
            resultado = geocodificar_territorio(territorio)
        except Exception:
            resultado = None
        if resultado is not None:
            novos_registros.append(resultado)

    if novos_registros:
        cache = pd.concat([cache, pd.DataFrame(novos_registros)], ignore_index=True).drop_duplicates(subset=["DscConjUndConsumidoras"], keep="last")
        cache.to_csv(GEO_CACHE_PATH, index=False)

    return cache


def gerar_mapa_tematico(territorios: pd.DataFrame) -> Path | None:
    destaque = territorios.dropna(subset=["score_vulnerabilidade"]).nlargest(TOP_N_MAPA, "score_vulnerabilidade").copy()
    geo = carregar_ou_geocodificar(destaque)
    geo = destaque.merge(geo, on="DscConjUndConsumidoras", how="inner")
    if geo.empty:
        return None

    geo["geometry"] = [Point(xy) for xy in zip(geo["lon"], geo["lat"])]
    geo_df = gpd.GeoDataFrame(geo, geometry="geometry", crs="EPSG:4326")

    mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=10, tiles="CartoDB positron")
    escala = linear.YlOrRd_09.scale(geo_df["score_vulnerabilidade"].min(), geo_df["score_vulnerabilidade"].max())
    escala.caption = "Média DEC + FEC"

    for _, linha in geo_df.iterrows():
        folium.CircleMarker(
            location=[linha["lat"], linha["lon"]],
            radius=6 + (float(linha["score_vulnerabilidade"]) * 1.5),
            color=escala(float(linha["score_vulnerabilidade"])),
            fill=True,
            fill_color=escala(float(linha["score_vulnerabilidade"])),
            fill_opacity=0.82,
            weight=1,
            popup=folium.Popup(
                f"<b>{linha['DscConjUndConsumidoras']}</b><br>DEC: {linha['media_dec']:.2f}<br>FEC: {linha['media_fec']:.2f}",
                max_width=300,
            ),
        ).add_to(mapa)

    escala.add_to(mapa)
    mapa.fit_bounds([[float(geo_df["lat"].min()) - 0.05, float(geo_df["lon"].min()) - 0.05], [float(geo_df["lat"].max()) + 0.05, float(geo_df["lon"].max()) + 0.05]])

    html_path = OUTPUT_DIR / "mapa_vulnerabilidade_sp.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(html_path))
    return html_path


def exportar_resultados(
    recorte: pd.DataFrame,
    qualidade: pd.DataFrame,
    describe_conjuntos: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    describe_conjuntos.to_csv(OUTPUT_DIR / "eletropaulo_2025_2026_describe_conjuntos.csv", index=False)

    print("\nBase resumida exportada em data/processed")


def main() -> None:
    print("Carregando base bruta...")
    df = carregar_dados_csv(CSV_PATH)
    base = preparar_base(df)

    print("Aplicando recorte: ELETROPAULO + anos 2025/2026 + DEC/FEC...")
    recorte = filtrar_recorte(base)

    print(f"Registros no recorte: {len(recorte):,}")
    print("Anos no recorte:", sorted(recorte["AnoIndice"].dropna().unique().tolist()))
    print("Indicadores no recorte:", sorted(recorte["SigIndicador"].dropna().unique().tolist()))

    qualidade = resumo_qualidade_dados(recorte)
    describe_conjuntos = describe_por_conjunto(recorte)

    exportar_resultados(recorte, qualidade, describe_conjuntos)

    print("\nDescribe por conjunto e indicador:")
    print(describe_conjuntos.head(20).to_string(index=False))
    print("\nArquivos exportados em data/processed")


if __name__ == "__main__":
    main()
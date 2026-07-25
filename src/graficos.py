from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import explore as base


CSV_DESCRIBE = Path("data/processed/eletropaulo_2025_2026_describe_conjuntos.csv")
OUTPUT_DIR = Path("data/processed/figures")
TOP_N = 10

sns.set_theme(style="whitegrid", context="talk")

CORES = {
    "DEC": "#8E1F2F",
    "FEC": "#1F5C87",
    "positivo": "#C0392B",
    "negativo": "#2E86C1",
    "fundo": "#F8F6F1",
    "texto": "#1F2933",
    "grade": "#D6D9DE",
}


def carregar_describe() -> pd.DataFrame:
    if not CSV_DESCRIBE.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {CSV_DESCRIBE}. Rode src/explore.py primeiro."
        )
    return pd.read_csv(CSV_DESCRIBE)


def resumo_por_territorio(describe_conjuntos: pd.DataFrame) -> pd.DataFrame:
    territorios = base.resumo_por_territorio(describe_conjuntos)
    return territorios


def salvar(fig: plt.Figure, nome: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho = OUTPUT_DIR / nome
    fig.patch.set_facecolor(CORES["fundo"])
    fig.savefig(caminho, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return caminho


def gerar_histograma(territorios: pd.DataFrame) -> Path:
    df = territorios[["DscConjUndConsumidoras", "media_dec", "media_fec"]].dropna().copy()
    media_sp_dec = df["media_dec"].mean()
    media_sp_fec = df["media_fec"].mean()

    fig, axes = plt.subplots(2, 1, figsize=(14, 12), constrained_layout=True)
    fig.suptitle(
        "Distribuição da continuidade por território",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, coluna, cor, titulo, media_sp in [
        (axes[0], "media_dec", CORES["DEC"], "DEC: duração das interrupções", media_sp_dec),
        (axes[1], "media_fec", CORES["FEC"], "FEC: frequência das interrupções", media_sp_fec),
    ]:
        dados = df[coluna].dropna()
        sns.histplot(
            dados,
            bins=18,
            ax=ax,
            color=cor,
            alpha=0.78,
            edgecolor="white",
            linewidth=0.8,
            kde=True,
        )
        ax.axvline(media_sp, color="#111111", linestyle="--", linewidth=1.7, label=f"Média SP: {media_sp:.2f}")
        ax.set_title(titulo, fontsize=15, fontweight="bold")
        ax.set_xlabel("Média por conjunto")
        ax.set_ylabel("Quantidade de territórios")
        ax.legend(frameon=True)
        ax.grid(True, axis="y", color=CORES["grade"], alpha=0.4)

    return salvar(fig, "01_histograma_dec_fec.png")


def _top_territorios(describe_conjuntos: pd.DataFrame, indicador: str) -> pd.DataFrame:
    subset = describe_conjuntos[describe_conjuntos["SigIndicador"].eq(indicador)].copy()
    return subset.nlargest(TOP_N, "media").sort_values("media")


def gerar_boxplot_customizado(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(14, 13), constrained_layout=True)
    fig.suptitle(
        "Anatomia da desigualdade: boxplots dos 10 territórios mais críticos",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador, cor in zip(axes, ["DEC", "FEC"], [CORES["DEC"], CORES["FEC"]]):
        subset = _top_territorios(describe_conjuntos, indicador)
        stats = [
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
            for _, row in subset.iterrows()
        ]
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
        ax.set_title(f"{indicador}: dispersão e extremos", fontsize=15, fontweight="bold")
        ax.set_xlabel("Índice")
        ax.set_ylabel("")
        ax.grid(True, axis="x", alpha=0.2)

    return salvar(fig, "02_boxplot_customizado.png")


def gerar_barras_divergentes(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(14, 13), constrained_layout=True)
    fig.suptitle(
        "Desvio em relação à média geral de São Paulo",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador, cor in zip(axes, ["DEC", "FEC"], [CORES["DEC"], CORES["FEC"]]):
        subset = describe_conjuntos[describe_conjuntos["SigIndicador"].eq(indicador)].copy()
        media_sp = subset["media"].mean()
        subset["delta"] = subset["media"] - media_sp
        subset = pd.concat(
            [subset.nsmallest(TOP_N, "delta"), subset.nlargest(TOP_N, "delta")],
            ignore_index=True,
        ).drop_duplicates(subset=["DscConjUndConsumidoras"])
        subset = subset.sort_values("delta")

        colors = [CORES["negativo"] if valor < 0 else CORES["positivo"] for valor in subset["delta"]]
        ax.barh(subset["DscConjUndConsumidoras"], subset["delta"], color=colors, alpha=0.92)
        ax.axvline(0, color=CORES["texto"], linewidth=1.2)
        ax.set_title(f"{indicador} - diferença frente à média SP ({media_sp:.3f})", fontsize=15, fontweight="bold")
        ax.set_xlabel("Diferença da média territorial")
        ax.set_ylabel("")
        ax.grid(True, axis="x", alpha=0.2)

    return salvar(fig, "03_barras_divergentes.png")


def gerar_error_bars(describe_conjuntos: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(14, 13), constrained_layout=True)
    fig.suptitle(
        "Incerteza territorial: média com desvio-padrão",
        fontsize=20,
        fontweight="bold",
        color=CORES["texto"],
    )

    for ax, indicador, cor in zip(axes, ["DEC", "FEC"], [CORES["DEC"], CORES["FEC"]]):
        subset = _top_territorios(describe_conjuntos, indicador)
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
        ax.set_title(f"{indicador} - média com intervalo de variação", fontsize=15, fontweight="bold")
        ax.set_xlabel("Índice")
        ax.set_ylabel("")
        ax.grid(True, axis="x", alpha=0.2)

    return salvar(fig, "04_error_bars.png")


def main() -> None:
    describe_conjuntos = carregar_describe()
    territorios = resumo_por_territorio(describe_conjuntos)

    figuras = [
        gerar_histograma(territorios),
        gerar_boxplot_customizado(describe_conjuntos),
        gerar_barras_divergentes(describe_conjuntos),
        gerar_error_bars(describe_conjuntos),
    ]

    print("Figuras geradas:")
    for figura in figuras:
        print(f"- {figura}")


if __name__ == "__main__":
    main()

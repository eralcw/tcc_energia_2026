"""Gráficos do Censo 2022 por distrito — São Paulo.

Design editorial (ver src/estilo.py): paleta quente, título em caixa alta,
anotação em itálico dentro do gráfico, grade pontilhada discreta.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

import estilo as st

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
FIG = PROC / "figures"


def _anotar_distrito(eixo, df, nome, desloc, ha="left"):
    linha = df[df["distrito"] == nome]
    if linha.empty:
        return
    x = linha["pct_negro"].iloc[0]
    y = linha["_y"].iloc[0]
    valor = linha["pct_negro"].iloc[0]
    eixo.annotate(
        f"{nome}\n{valor:.0f}%", xy=(x, y), xytext=desloc, textcoords="offset points",
        fontsize=9.8, color=st.TINTA, ha=ha, va="center", linespacing=1.35,
        arrowprops=dict(arrowstyle="-", color="#b5b5b5", linewidth=0.7,
                        shrinkA=0, shrinkB=4),
        zorder=5,
    )


def grafico_cidade_partida(df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(10.5, 5.7))
    eixo = fig.add_axes([0.055, 0.19, 0.90, 0.62])

    rng = np.random.default_rng(11)
    df = df.copy()
    df["_y"] = rng.uniform(0.04, 0.96, len(df))

    x = df["pct_negro"].values
    norm = (x - x.min()) / (x.max() - x.min())
    tamanho = (df["populacao"] / df["populacao"].max()) ** 0.5 * 520 + 35

    eixo.scatter(x, df["_y"], s=tamanho, c=st.GRADIENTE(norm),
                 alpha=0.92, edgecolor="white", linewidth=0.6, zorder=3)

    mediana = df["pct_negro"].median()
    eixo.axvline(mediana, color=st.TINTA, linewidth=0.9,
                 linestyle=(0, (2, 3)), zorder=2)
    eixo.text(mediana + 1.0, 1.015, f"mediana da cidade · {mediana:.0f}%",
              transform=eixo.get_xaxis_transform(), fontsize=9.0,
              color=st.GRAFITE, ha="left", va="bottom")

    _anotar_distrito(eixo, df, "Moema", (-14, 34), ha="right")
    _anotar_distrito(eixo, df, "Jardim Ângela", (14, 36), ha="left")
    _anotar_distrito(eixo, df, "Parelheiros", (16, -30), ha="left")

    eixo.set_xlim(0, 72)
    eixo.set_ylim(0, 1)
    eixo.set_yticks([])
    eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    eixo.set_xticks([0, 10, 20, 30, 40, 50, 60, 70])
    st.grade_vertical(eixo)
    st.soltar(eixo, esquerda=False)
    eixo.spines["left"].set_visible(False)
    eixo.set_xlabel("população preta + parda por distrito", fontsize=9.8,
                    color=st.GRAFITE, labelpad=10)
    st.dica(eixo, "menos negra", "mais negra")

    h1 = eixo.scatter([], [], s=45, color=st.CINZA, alpha=0.8, edgecolor="white")
    h2 = eixo.scatter([], [], s=280, color=st.CINZA, alpha=0.8, edgecolor="white")
    st.legenda(eixo, [h1, h2], ["menor população", "maior população"],
               loc="upper left", ancora=(0.0, 1.05), ncol=2)

    st.regua(fig)
    st.titulo(fig, "A cidade partida")
    st.subtitulo(fig, "Cada ponto é um dos 96 distritos de São Paulo. O tamanho indica a população.", 0.895)
    st.fonte(fig, "fonte: IBGE, Censo Demográfico 2022 · elaboração própria")

    fig.savefig(FIG / "ibge_01_extremos_populacao_negra.png", dpi=300,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


def grafico_negro_x_lixo(df: pd.DataFrame) -> None:
    col = "pct_lixo_sem_coleta"
    fig = plt.figure(figsize=(10.5, 6.0))
    eixo = fig.add_axes([0.085, 0.18, 0.80, 0.63])

    x = df["pct_negro"].values
    norm = (x - x.min()) / (x.max() - x.min())
    tamanho = (df["populacao"] / df["populacao"].max()) ** 0.5 * 520 + 35
    eixo.scatter(x, df[col], s=tamanho, c=st.GRADIENTE(norm),
                 alpha=0.9, edgecolor="white", linewidth=0.8, zorder=3)

    # linhas de referência: mediana de cada terço (como as linhas anotadas do original)
    df = df.copy()
    df["terco"] = pd.qcut(df["pct_negro"], 3, labels=["baixo", "medio", "alto"])
    baixo = df.loc[df.terco == "baixo", col].median()
    alto = df.loc[df.terco == "alto", col].median()

    for valor, rotulo, desloc in [
        (baixo, f"terço menos negro · {baixo:.2f}%", 0.0),
        (alto, f"terço mais negro · {alto:.2f}%", 0.0),
    ]:
        eixo.plot([4, 70], [valor, valor], color=st.TINTA, linewidth=0.9, zorder=2)
        eixo.text(71, valor + desloc, rotulo, fontsize=9.0, color=st.GRAFITE,
                  ha="left", va="center")

    eixo.set_xlim(0, 88)
    eixo.set_ylim(-0.08, 2.85)
    eixo.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    eixo.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}%"))
    eixo.set_xticks([0, 10, 20, 30, 40, 50, 60, 70])
    st.grade_vertical(eixo)
    st.soltar(eixo)
    eixo.set_xlabel("população preta + parda por distrito", fontsize=9.8,
                    color=st.GRAFITE, labelpad=10)
    eixo.set_ylabel("domicílios sem coleta de lixo", fontsize=9.8,
                    color=st.GRAFITE, labelpad=10)
    st.dica(eixo, "menos negra", "mais negra")

    st.anotacao(eixo, 4, 2.42,
                "No terço mais negro, a falta de coleta\né cerca de 30 vezes maior.",
                va="top", tamanho=11.0)

    r = df[["pct_negro", col]].corr(method="spearman").iloc[0, 1]
    eixo.text(0.995, 0.965, f"Spearman ρ = {r:.2f}", transform=eixo.transAxes,
              fontsize=9.4, color=st.CINZA, ha="right", va="top")

    h1 = eixo.scatter([], [], s=45, color=st.CINZA, alpha=0.8, edgecolor="white")
    h2 = eixo.scatter([], [], s=280, color=st.CINZA, alpha=0.8, edgecolor="white")
    st.legenda(eixo, [h1, h2], ["menor população", "maior população"],
               loc="upper left", ancora=(0.0, 1.05), ncol=2)

    st.regua(fig)
    st.titulo(fig, "Onde a pele é preta, falta coleta")
    st.subtitulo(fig, "Domicílios sem coleta de lixo e população negra, por distrito. Tamanho do ponto = população.", 0.895)
    st.fonte(fig, "fonte: IBGE, Censo Demográfico 2022 · elaboração própria")

    fig.savefig(FIG / "ibge_02_negro_x_lixo.png", dpi=300,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    st.configurar()
    FIG.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC / "ibge_distritos_sp.csv", encoding="utf-8-sig")
    grafico_cidade_partida(df)
    grafico_negro_x_lixo(df)
    print("Figuras geradas em", FIG)
    for arq in sorted(FIG.glob("ibge_*.png")):
        print("  -", arq.name)


if __name__ == "__main__":
    main()

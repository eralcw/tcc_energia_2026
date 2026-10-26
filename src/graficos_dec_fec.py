"""Gráficos de DEC/FEC e da experiência — recorte 2023-2026.

Mesma linguagem editorial dos gráficos do IBGE (src/estilo.py), com legendas
explícitas porque a leitura é de banca de Ciências Sociais, não de engenharia.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

import estilo as st

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"
FIG = PROC / "figures"


def _marcador(cor, tamanho=9.4):
    return Line2D([0], [0], marker="o", color="none", markerfacecolor=cor,
                  markeredgecolor="white", markeredgewidth=1.2, markersize=tamanho)


def grafico_indicador_parado(painel: pd.DataFrame) -> None:
    cap = painel[(painel.municipio == "capital") & (~painel.parcial)]
    med = cap.groupby("AnoIndice").DEC.median()
    p90 = cap.groupby("AnoIndice").DEC.quantile(0.9)
    parcial = painel[(painel.municipio == "capital") & painel.parcial].DEC.median()

    anos = [2023, 2024, 2025]
    x = [0, 1, 2]

    fig = plt.figure(figsize=(10.5, 6.2))
    eixo = fig.add_axes([0.085, 0.22, 0.80, 0.57])

    linha_med, = eixo.plot(x, [med[a] for a in anos], color=st.VERDE_AGUA, linewidth=2.2,
                           marker="o", markersize=7, markeredgecolor="white",
                           markeredgewidth=1.4, zorder=3)
    linha_p90, = eixo.plot(x, [p90[a] for a in anos], color=st.TERRACOTA, linewidth=2.2,
                           marker="o", markersize=7, markeredgecolor="white",
                           markeredgewidth=1.4, zorder=3)

    eixo.text(2.08, p90[2025], f"p90 · {p90[2025]:.1f} h", color=st.TERRACOTA,
              fontsize=10.6, va="center", ha="left")
    eixo.text(2.08, med[2025], f"mediana · {med[2025]:.1f} h", color=st.VERDE_AGUA,
              fontsize=10.6, va="center", ha="left")

    eixo.axvline(2.72, color="#cfcfcf", linewidth=1, linestyle=(0, (2, 2)))
    eixo.plot([3.22], [parcial], marker="o", markersize=8, markerfacecolor="white",
              markeredgecolor=st.CINZA, markeredgewidth=1.6, linestyle="none", zorder=3)
    eixo.text(3.30, parcial, "2026\n5 meses", color=st.CINZA, fontsize=9.0,
              va="center", ha="left", linespacing=1.4)

    eixo.set_xticks([0, 1, 2, 3.22])
    eixo.set_xticklabels(["2023", "2024", "2025", "2026"])
    eixo.set_xlim(-0.35, 4.30)
    eixo.set_ylim(0, 12)
    eixo.set_ylabel("horas sem energia por unidade consumidora (h/ano)",
                    fontsize=9.8, color=st.GRAFITE, labelpad=10)
    st.grade_horizontal(eixo)
    st.soltar(eixo)
    eixo.spines["bottom"].set_visible(False)
    eixo.tick_params(axis="x", pad=8)

    st.anotacao(eixo, -0.2, 11.4,
                "Entre 2023 e 2025 o indicador oficial quase não se move —\n"
                "enquanto 16.354 interrupções da concessão passaram de 24 h em 2025.",
                va="top", tamanho=10.9)

    st.legenda(eixo, [linha_med, linha_p90],
               ["mediana dos conjuntos", "p90 — os 10% piores"], loc="lower left")

    st.regua(fig)
    st.titulo(fig, "O indicador não sente a crise")
    st.subtitulo(fig, "DEC = horas sem energia por unidade consumidora no ano. Cada linha resume os 122 conjuntos da capital.", 0.895)
    st.fonte(fig, "fonte: ANEEL, indicadores coletivos de continuidade · elaboração própria")

    fig.savefig(FIG / "dec_01_indicador_parado.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _ranking(painel: pd.DataFrame, coluna: str, titulo_txt: str, subtitulo_txt: str,
             arquivo: str, unidade: str, rotulo_eixo: str) -> None:
    d = painel[(painel.municipio == "capital") & (painel.AnoIndice == 2025) & (~painel.parcial)]
    d = d.nlargest(15, coluna).sort_values(coluna)

    fig = plt.figure(figsize=(10.5, 6.4))
    eixo = fig.add_axes([0.30, 0.17, 0.62, 0.62])

    norm = (d[coluna] - d[coluna].min()) / (d[coluna].max() - d[coluna].min())
    cores = st.GRADIENTE(0.25 + 0.75 * norm)
    y = np.arange(len(d))

    eixo.hlines(y, 0, d[coluna], color="#e2e2e2", linewidth=1.2, zorder=1)
    eixo.scatter(d[coluna], y, s=190, c=cores, edgecolor="white", linewidth=1.4, zorder=3)
    for yi, valor in zip(y, d[coluna]):
        eixo.text(valor + d[coluna].max() * 0.025, yi, f"{valor:.1f}".replace(".", ","),
                  va="center", fontsize=10.0, color=st.GRAFITE)

    eixo.set_yticks(y)
    eixo.set_yticklabels(d.DscConjUndConsumidoras, fontsize=10.0)
    eixo.set_xlim(0, d[coluna].max() * 1.18)
    eixo.set_xticks(np.arange(0, d[coluna].max() * 1.18, 5))
    eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    eixo.set_ylim(-0.8, len(d) - 0.2)
    eixo.set_xlabel(rotulo_eixo, fontsize=9.8, color=st.GRAFITE, labelpad=10)
    st.grade_vertical(eixo)
    st.soltar(eixo, esquerda=False)
    eixo.spines["left"].set_visible(False)
    eixo.tick_params(axis="y", pad=6)
    st.legenda(eixo, [_marcador(st.TERRACOTA, 6.5)], [f"cada ponto é um conjunto da capital · {unidade}"],
               loc="upper left", ancora=(0.0, 1.04))

    st.regua(fig)
    st.titulo(fig, titulo_txt, tamanho=17)
    st.subtitulo(fig, subtitulo_txt, 0.90)
    st.fonte(fig, "fonte: ANEEL, indicadores coletivos de continuidade · elaboração própria")

    fig.savefig(FIG / arquivo, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def grafico_concentracao(painel: pd.DataFrame) -> None:
    _ranking(
        painel, "DEC", "A escuridão se concentra",
        "Quinze conjuntos com maior DEC em 2025 — todos fora do centro expandido.",
        "dec_02_concentracao.png", "DEC 2025", "DEC em 2025 (horas sem energia por ano)",
    )


def grafico_concentracao_fec(painel: pd.DataFrame) -> None:
    _ranking(
        painel, "FEC", "A luz cai mais vezes nos mesmos lugares",
        "Quinze conjuntos com maior FEC em 2025 — o número de quedas no ano.",
        "dec_05_fec_ranking.png", "FEC 2025", "FEC em 2025 (vezes que a luz caiu no ano)",
    )


def grafico_frequencia_duracao(painel: pd.DataFrame) -> None:
    d = painel[(painel.municipio == "capital") & (painel.AnoIndice == 2025) & (~painel.parcial)]
    md, mf = d.DEC.median(), d.FEC.median()

    fig = plt.figure(figsize=(10.5, 6.6))
    eixo = fig.add_axes([0.085, 0.18, 0.78, 0.60])

    norm = (d.DEC - d.DEC.min()) / (d.DEC.max() - d.DEC.min())
    tamanho = (d.DEC / d.DEC.max()) ** 0.5 * 90 + 55
    eixo.scatter(d.DEC, d.FEC, s=tamanho, c=st.GRADIENTE(0.15 + 0.8 * norm),
                 alpha=0.9, edgecolor="white", linewidth=0.8, zorder=3)

    eixo.axvline(md, color="#bdbdbd", linewidth=0.9, linestyle=(0, (2, 3)), zorder=1)
    eixo.axhline(mf, color="#bdbdbd", linewidth=0.9, linestyle=(0, (2, 3)), zorder=1)

    quadrantes = [
        (0.985, 0.965, "cai muito e demora", "right", "top"),
        (0.015, 0.965, "cai muito, mas volta rápido", "left", "top"),
        (0.985, 0.025, "cai pouco, mas quando cai, demora", "right", "bottom"),
        (0.015, 0.265, "raro e curto", "left", "top"),
    ]
    for x, y, texto, ha, va in quadrantes:
        eixo.text(x, y, texto, transform=eixo.transAxes, fontsize=10.0,
                  color=st.CINZA, style="italic", fontfamily=st.FONTE_SERIFA,
                  ha=ha, va=va)

    for nome, desloc, ha in [("RAPOSO TAVARES", (-10, 6), "right"),
                             ("RIO GRANDE", (-8, 12), "right"),
                             ("PARELHEIROS", (10, 6), "left"),
                             ("VARGEM GRANDE", (0, -22), "center")]:
        linha = d[d.DscConjUndConsumidoras == nome]
        if linha.empty:
            continue
        eixo.annotate(nome.title(), (linha.DEC.iloc[0], linha.FEC.iloc[0]),
                      textcoords="offset points", xytext=desloc, fontsize=9.2,
                      color=st.TINTA, ha=ha)

    eixo.set_xlim(0, 18)
    eixo.set_ylim(0, 21)
    eixo.set_xlabel("DEC — horas sem energia no ano", fontsize=10.0, color=st.GRAFITE, labelpad=8)
    eixo.set_ylabel("FEC — vezes que a luz caiu no ano", fontsize=10.0, color=st.GRAFITE, labelpad=8)
    st.soltar(eixo)

    st.legenda(eixo, [_marcador(st.TERRACOTA, 7)],
               ["um conjunto da capital em 2025"], loc="upper center", ancora=(0.47, 1.0))

    st.regua(fig)
    st.titulo(fig, "Duração e frequência não contam a mesma história", tamanho=16)
    st.subtitulo(fig, "As linhas tracejadas marcam a mediana da cidade: DEC 6,0 h e FEC 2,9 quedas.", 0.895)
    st.fonte(fig, "fonte: ANEEL, indicadores coletivos de continuidade 2025 · elaboração própria")

    fig.savefig(FIG / "dec_04_frequencia_duracao.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def grafico_cauda(eventos: pd.DataFrame) -> None:
    dur = eventos.duracao_h.clip(lower=0.01)
    bins = np.logspace(np.log10(0.01), np.log10(300), 70)

    fig = plt.figure(figsize=(10.5, 6.2))
    eixo = fig.add_axes([0.085, 0.21, 0.84, 0.56])

    n, edges, patches = eixo.hist(dur, bins=bins, color=st.VERDE_CLARO, edgecolor="white", linewidth=0.4)
    for patch, esquerda in zip(patches, edges[:-1]):
        if esquerda >= 24:
            patch.set_facecolor(st.TERRACOTA)

    eixo.set_xscale("log")
    eixo.set_xlim(0.01, 300)
    eixo.set_ylim(0, n.max() * 1.18)

    for valor, rotulo in [(24, "24 h"), (48, "48 h"), (72, "72 h")]:
        eixo.axvline(valor, color=st.TINTA, linewidth=0.8, linestyle=(0, (2, 3)), zorder=2)
        eixo.text(valor, n.max() * 1.02, rotulo, fontsize=8.4, color=st.GRAFITE,
                  ha="center", va="bottom", rotation=90)

    total = len(eventos)
    cauda = (eventos.duracao_h >= 24).sum()
    st.anotacao(eixo, 0.012, n.max() * 0.92,
                f"{cauda:,} quedas passaram de 24 h\n{100*cauda/total:.1f}% do total".replace(",", "."),
                va="top", tamanho=11.0)
    st.anotacao(eixo, 78, n.max() * 0.30, "a maior:\n168,8 h", ha="center", va="top", tamanho=10.6)

    eixo.set_xlabel("duração de cada interrupção (horas, escala logarítmica)",
                    fontsize=9.8, color=st.GRAFITE, labelpad=10)
    eixo.set_ylabel("número de interrupções", fontsize=9.8, color=st.GRAFITE, labelpad=10)
    eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    eixo.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    st.soltar(eixo)

    st.legenda(eixo,
               [Patch(facecolor=st.VERDE_CLARO, edgecolor="white"),
                Patch(facecolor=st.TERRACOTA, edgecolor="white")],
               ["até 24 horas", "mais de 24 horas — a cauda"], loc="upper left")

    st.regua(fig)
    st.titulo(fig, "A cauda que o índice não mostra")
    st.subtitulo(fig, "Duração das 473 mil interrupções da Eletropaulo em 2025 — cada barra é uma faixa de duração.", 0.895)
    st.fonte(fig, "fonte: ANEEL, interrupções de energia elétrica 2025 · elaboração própria")

    fig.savefig(FIG / "dec_03_cauda.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    st.configurar()
    painel = pd.read_csv(PROC / "dec_fec_tratado.csv", encoding="utf-8-sig")
    grafico_indicador_parado(painel)
    grafico_concentracao(painel)
    grafico_concentracao_fec(painel)
    grafico_frequencia_duracao(painel)

    caminho_eventos = PROC / "eventos_eletropaulo_2025.csv"
    if caminho_eventos.exists():
        grafico_cauda(pd.read_csv(caminho_eventos, encoding="utf-8-sig"))
    else:
        print("aviso: eventos ausentes — gráfico da cauda não gerado")

    print("Figuras geradas:")
    for arq in sorted(FIG.glob("dec_*.png")):
        print("  -", arq.name)


if __name__ == "__main__":
    main()

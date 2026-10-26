"""Base visual dos gráficos do TCC.

Linguagem editorial: paleta quente (verde-água -> creme -> terracota), título
em caixa alta espaçada, anotações em itálico dentro do gráfico, grade pontilhada
discreta e muito espaço branco. Nada de caixa em volta, nada de legenda quando
o rótulo direto resolve.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# --- paleta ---------------------------------------------------------------
TINTA = "#1c1c1c"
GRAFITE = "#4a4a4a"
CINZA = "#8f8f8f"
CINZA_CLARO = "#dcdcdc"

VERDE_AGUA = "#17798a"
VERDE_CLARO = "#8fc3c9"
CREME = "#f0e2d3"
SALMAO = "#e2a184"
TERRACOTA = "#bd441b"
TERRACOTA_ESCURO = "#8f2f12"

PALETA = [VERDE_AGUA, VERDE_CLARO, CREME, SALMAO, TERRACOTA]
GRADIENTE = LinearSegmentedColormap.from_list("tcc", PALETA)

FONTE = "DejaVu Sans"
FONTE_SERIFA = "DejaVu Serif"


def configurar() -> None:
    plt.rcParams.update({
        "font.family": FONTE,
        "font.size": 9,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": CINZA_CLARO,
        "axes.labelcolor": GRAFITE,
        "text.color": TINTA,
        "xtick.color": CINZA,
        "ytick.color": CINZA,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.labelcolor": GRAFITE,
        "ytick.labelcolor": GRAFITE,
    })


def espacar(texto: str) -> str:
    """Caixa alta com espaçamento entre letras (efeito editorial)."""
    return " ".join(texto.upper())


def titulo(fig, texto: str, y: float = 0.96, tamanho: int = 17) -> None:
    fig.text(0.02, y, espacar(texto), fontsize=tamanho, color=TINTA,
             ha="left", va="top", fontweight="medium")


def subtitulo(fig, texto: str, y: float = 0.905) -> None:
    fig.text(0.02, y, texto, fontsize=11.4, color=GRAFITE, style="italic",
             ha="left", va="top")


def regua(fig, x: float = 0.02, y: float = 0.985, largura: float = 0.045) -> None:
    """Pequeno traço colorido acima do título."""
    fig.add_artist(plt.Line2D([x, x + largura], [y, y], color=TERRACOTA,
                              linewidth=2.2, transform=fig.transFigure))


def anotacao(eixo, x, y, texto, ha="left", va="center", cor=None, tamanho=10.6, desloc=(0, 0)):
    eixo.annotate(
        texto, xy=(x, y), xytext=desloc, textcoords="offset points",
        fontsize=tamanho, color=cor or GRAFITE, fontfamily=FONTE_SERIFA,
        style="italic", ha=ha, va=va,
    )


def fonte(fig, texto: str, y: float = 0.012) -> None:
    fig.text(0.02, y, espacar(texto), fontsize=8.0, color=CINZA, ha="left", va="bottom")


def grade_vertical(eixo, cor: str = "#e6e6e6") -> None:
    eixo.grid(axis="x", color=cor, linewidth=0.8, linestyle=(0, (1, 3)))
    eixo.set_axisbelow(True)


def grade_horizontal(eixo, cor: str = "#e6e6e6") -> None:
    eixo.grid(axis="y", color=cor, linewidth=0.8, linestyle=(0, (1, 3)))
    eixo.set_axisbelow(True)


def soltar(eixo, esquerda: bool = True) -> None:
    """Remove molduras; mantém só o eixo que carrega a leitura."""
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    eixo.spines["bottom"].set_color("#cfcfcf")
    eixo.spines["left"].set_visible(esquerda)
    if esquerda:
        eixo.spines["left"].set_color("#cfcfcf")


def dica(eixo, esquerda: str, direita: str) -> None:
    """Rótulos de direção nas pontas do eixo (estilo 'MAIS NEGRO ->')."""
    eixo.text(0, -0.11, espacar(esquerda), transform=eixo.transAxes,
              fontsize=8.0, color=CINZA, ha="left", va="top")
    eixo.text(1, -0.11, espacar(direita), transform=eixo.transAxes,
              fontsize=8.0, color=CINZA, ha="right", va="top")


def legenda(eixo, handles, rotulos, loc="upper left", ncol=1, titulo=None, tamanho=9.2, ancora=None):
    """Legenda discreta, sem caixa — para a banca ler sem esforço."""
    leg = eixo.legend(
        handles, rotulos, loc=loc, frameon=False, fontsize=tamanho,
        handletextpad=0.9, labelspacing=0.7, ncol=ncol, borderaxespad=0.8,
        title=titulo, bbox_to_anchor=ancora,
    )
    if titulo:
        leg.get_title().set_fontsize(7.2)
        leg.get_title().set_color(GRAFITE)
    for texto in leg.get_texts():
        texto.set_color(GRAFITE)
    return leg

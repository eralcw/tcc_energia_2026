from pathlib import Path
import webbrowser


MAPA_PATH = Path("data/processed/mapa_vulnerabilidade_sp.html")


def main() -> None:
    caminho = MAPA_PATH.resolve()
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho}. Rode src/explore.py primeiro para gerar o mapa."
        )

    webbrowser.open(caminho.as_uri())
    print(f"Mapa aberto no navegador: {caminho}")


if __name__ == "__main__":
    main()

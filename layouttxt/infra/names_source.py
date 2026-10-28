"""Lista de sobrenomes usada pelo gerador de nomes aleatórios."""

from __future__ import annotations

from pathlib import Path

from layouttxt.infra.ansi_text import AnsiFileStore

DEFAULT_NAMES_PATH = Path(__file__).resolve().parent.parent / "resources" / "Nomes.txt"


def load_names(store: AnsiFileStore, path: Path = DEFAULT_NAMES_PATH) -> list[str]:
    """Nomes não vazios do arquivo; lista vazia se ele não puder ser lido.

    Exemplo:
        >>> load_names(AnsiFileStore())[:2]  # doctest: +SKIP
        ['AAH', 'ABREU']
    """
    try:
        content = store.read(str(path)).content
    except OSError:
        return []
    return [line.strip() for line in content.split("\n") if line.strip()]

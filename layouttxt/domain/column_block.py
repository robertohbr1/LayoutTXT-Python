"""Blocos de colunas: copiar um retângulo e colar texto em coluna."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from layouttxt.domain.layout import FieldSpec
from layouttxt.domain.text_search import TextPosition


def extract_block(lines: Sequence[str], corner_a: TextPosition, corner_b: TextPosition) -> str:
    """Texto do retângulo entre dois cantos (inclusive), uma linha por linha.

    Exemplo:
        >>> extract_block(["abcd", "efgh"], TextPosition(2, 3), TextPosition(1, 2))
        'bc\\nfg\\n'
    """
    first_line, last_line = sorted((corner_a.line, corner_b.line))
    first_col, last_col = sorted((corner_a.column, corner_b.column))
    selected = lines[first_line - 1 : last_line]
    return "".join(line[first_col - 1 : last_col] + "\n" for line in selected)


def paste_block(lines: Sequence[str], at: TextPosition, clip_text: str, insert_mode: bool) -> list[str]:
    """Cola cada linha do texto na mesma coluna das linhas seguintes (`ColaTexto`).

    Na coluna 1 em modo Insere com várias linhas, elas são inseridas como
    linhas novas. Linhas curtas são completadas com espaços.

    Exemplo:
        >>> paste_block(["abc", "def"], TextPosition(1, 2), "X\\nY", False)
        ['aXc', 'dYf']
    """
    pieces = _clip_lines(clip_text)
    if not pieces:
        return list(lines)
    if at.column == 1 and insert_mode and len(pieces) > 1:
        return list(lines[: at.line - 1]) + pieces + list(lines[at.line - 1 :])
    result = list(lines) + [""] * max(0, at.line - 1 + len(pieces) - len(lines))
    for offset, piece in enumerate(pieces):
        index = at.line - 1 + offset
        result[index] = _paste_into(result[index], at.column, piece, insert_mode)
    return result


def _clip_lines(clip_text: str) -> list[str]:
    pieces = clip_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    # Uma quebra final no clipboard não deve virar uma linha vazia extra.
    return pieces[:-1] if pieces and pieces[-1] == "" else pieces


def _paste_into(line: str, column: int, piece: str, insert_mode: bool) -> str:
    offset = column - 1
    padded = line.ljust(offset)
    tail_start = offset if insert_mode else min(len(padded), offset + len(piece))
    return padded[:offset] + piece + padded[tail_start:]


def field_values(
    lines: Sequence[str], line_types: Sequence[str], record_id: str, field: FieldSpec
) -> list[tuple[str, int]]:
    """Pares (valor, linha 1-based) do campo nas linhas do tipo, ordenados por valor.

    Exemplo:
        >>> f = FieldSpec("D", "x", 2, 2, 1, "C", "", "", "")
        >>> field_values(["Db", "Da", "H"], ["D", "D", "H"], "D", f)
        [('a', 2), ('b', 1)]
    """
    pairs = [(field.extract(line), number) for number, (line, line_type) in enumerate(zip(lines, line_types), 1)]
    return sorted(pair for pair, line_type in zip(pairs, line_types) if line_type == record_id)


def count_values(values: Sequence[str]) -> list[tuple[str, int]]:
    """Quantidade de cada valor distinto, ordenado por valor ("Conta Valores").

    Exemplo:
        >>> count_values(["b", "a", "b"])
        [('a', 1), ('b', 2)]
    """
    return sorted(Counter(values).items())

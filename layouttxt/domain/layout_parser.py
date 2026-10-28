"""Leitura do CSV de layout (`Id;Nome;Inic;Fim;Tam;TP;Fixo;Formato;Tag`)."""

from __future__ import annotations

from layouttxt.domain.layout import FieldSpec, Layout

EXPECTED_HEADER: tuple[str, ...] = (
    "Id",
    "Nome",
    "Inic",
    "Fim",
    "Tam",
    "TP",
    "Fixo",
    "Formato",
    "Tag",
)
SEPARATOR = ";"


class LayoutFormatError(ValueError):
    """CSV de layout fora do formato esperado."""


def parse_layout(csv_text: str) -> Layout:
    """Converte o texto de um CSV de layout em `Layout`.

    Assim como no VB, só as 9 primeiras colunas são consideradas; colunas
    extras (ex.: `;` dentro da descrição) são ignoradas.

    Exemplo:
        >>> parse_layout("Id;Nome;Inic;Fim;Tam;TP;Fixo;Formato;Tag\\n0;T;1;1;1;F;0;;X").record_ids()
        ['0']
    """
    lines = csv_text.splitlines()
    if not lines:
        raise LayoutFormatError("Arquivo de layout vazio; esperado cabeçalho " + SEPARATOR.join(EXPECTED_HEADER))
    _check_header(lines[0])
    fields = [
        _parse_row(row, number)
        for number, row in enumerate(lines[1:], start=2)
        if row.replace(SEPARATOR, "").strip()
    ]
    return Layout(tuple(fields))


def _check_header(header: str) -> None:
    columns = tuple(header.split(SEPARATOR)[: len(EXPECTED_HEADER)])
    if columns != EXPECTED_HEADER:
        raise LayoutFormatError(
            "Arquivo com estrutura diferente da esperada\n"
            f"Esperada:    {SEPARATOR.join(EXPECTED_HEADER)}\n"
            f"Encontrada: {header}"
        )


def _parse_row(row: str, line_number: int) -> FieldSpec:
    cells = (row.split(SEPARATOR) + [""] * len(EXPECTED_HEADER))[: len(EXPECTED_HEADER)]
    start = _to_int(cells[2], "Inic", line_number)
    size = _to_int(cells[4], "Tam", line_number)
    end = _to_int(cells[3], "Fim", line_number) if cells[3].strip() else start + size - 1
    return FieldSpec(
        record_id=cells[0],
        name=cells[1],
        start=start,
        end=end,
        size=size,
        field_type=cells[5],
        fixed=cells[6],
        description=cells[7],
        tag=cells[8],
    )


def _to_int(cell: str, column: str, line_number: int) -> int:
    try:
        return int(cell.strip())
    except ValueError:
        raise LayoutFormatError(
            f"Linha {line_number}: coluna {column}={cell!r} inválida; esperado número inteiro"
        ) from None

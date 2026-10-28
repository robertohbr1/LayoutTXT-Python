"""Contexto do cursor: tipo de linha e campo sob a coluna atual."""

from __future__ import annotations

from dataclasses import dataclass

from layouttxt.domain.layout import FieldSpec, Layout


@dataclass(frozen=True)
class FieldContext:
    """Situação do cursor numa linha (equivale a `strIdAtual`/`rst` posicionado).

    `line_number` e `column` são 1-based.
    """

    line_number: int
    column: int
    line: str
    record_id: str
    fields: tuple[FieldSpec, ...]
    field: FieldSpec | None

    @property
    def value(self) -> str:
        """Conteúdo do campo atual na linha ("" sem campo)."""
        return self.field.extract(self.line) if self.field else ""


def resolve_context(layout: Layout | None, line: str, line_number: int, column: int) -> FieldContext:
    """Identifica o tipo da linha e o campo que contém a coluna.

    Exemplo:
        >>> resolve_context(None, "abc", 1, 1).record_id
        ''
    """
    record_id = layout.identify(line) if layout else ""
    if not record_id or layout is None:
        return FieldContext(line_number, column, line, "", (), None)
    fields = tuple(layout.fields_of(record_id))
    field = layout.field_at(record_id, column)
    return FieldContext(line_number, column, line, record_id, fields, field)


def replace_field(line: str, field: FieldSpec, value: str) -> str:
    """Grava `value` no campo, completando com espaços ou truncando em `size`.

    Se a linha for menor que o campo, ela é completada com espaços.

    Exemplo:
        >>> replace_field("AB", FieldSpec("0", "n", 3, 5, 3, "C", "", "", ""), "x")
        'ABx  '
    """
    return overwrite_at(line, field.start, value.ljust(field.size)[: field.size])


def overwrite_at(line: str, column: int, text: str) -> str:
    """Sobrescreve `text` a partir da coluna (1-based), completando a linha.

    Exemplo:
        >>> overwrite_at("abc", 5, "Z")
        'abc Z'
    """
    offset = column - 1
    padded = line.ljust(offset)
    return padded[:offset] + text + padded[offset + len(text) :]

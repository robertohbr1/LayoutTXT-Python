"""Busca de texto restrita por tipo de linha e campo, e filtros de linhas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Sequence


class SearchScope(Enum):
    """Onde uma ocorrência é aceita."""

    ALL = "Geral"
    LINE_TYPE = "Tp Linha"
    FIELD = "Campo"
    FIELD_START = "Início do campo"


@dataclass(frozen=True)
class TextPosition:
    """Posição 1-based (linha, coluna) no texto."""

    line: int
    column: int


@dataclass(frozen=True)
class SearchFilter:
    """Critério de aceitação de uma ocorrência.

    Exemplo:
        >>> SearchFilter(SearchScope.ALL).accepts(TextPosition(1, 1), 3)
        True
    """

    scope: SearchScope
    line_types: Sequence[str] = ()
    record_id: str = ""
    field_start: int = 0
    field_size: int = 0

    def accepts(self, position: TextPosition, length: int) -> bool:
        """True se a ocorrência em `position` com `length` caracteres vale."""
        if self.scope is SearchScope.ALL:
            return True
        if not self._same_line_type(position.line):
            return False
        if self.scope is SearchScope.FIELD_START:
            return position.column == self.field_start
        if self.scope is SearchScope.FIELD:
            return self._inside_field(position.column, length)
        return True

    def _same_line_type(self, line_number: int) -> bool:
        index = line_number - 1
        return 0 <= index < len(self.line_types) and self.line_types[index] == self.record_id

    def _inside_field(self, column: int, length: int) -> bool:
        return column >= self.field_start and column + length <= self.field_start + self.field_size


def iter_matches(lines: Sequence[str], needle: str, start: TextPosition) -> Iterator[TextPosition]:
    """Ocorrências (sem diferenciar maiúsculas) a partir de `start`, inclusive."""
    if not needle:
        return
    wanted = needle.lower()
    for index in range(max(start.line, 1) - 1, len(lines)):
        first_column = start.column if index == start.line - 1 else 1
        yield from _matches_in_line(lines[index].lower(), wanted, index + 1, first_column)


def find_next(
    lines: Sequence[str], needle: str, start: TextPosition, search_filter: SearchFilter
) -> TextPosition | None:
    """Primeira ocorrência aceita a partir de `start` (equivale a `Find`).

    Exemplo:
        >>> find_next(["abc", "xbc"], "BC", TextPosition(1, 3), SearchFilter(SearchScope.ALL))
        TextPosition(line=2, column=2)
    """
    for position in iter_matches(lines, needle, start):
        if search_filter.accepts(position, len(needle)):
            return position
    return None


def find_occurrences(lines: Sequence[str], needle: str, search_filter: SearchFilter) -> list[TextPosition]:
    """Todas as ocorrências aceitas, sem sobreposição (usado em "Marcar iguais")."""
    found: list[TextPosition] = []
    last: TextPosition | None = None
    for position in iter_matches(lines, needle, TextPosition(1, 1)):
        if last and _overlaps(last, position, len(needle)):
            continue
        last = position
        if search_filter.accepts(position, len(needle)):
            found.append(position)
    return found


def lines_of_type(lines: Sequence[str], line_types: Sequence[str], record_id: str) -> list[str]:
    """Linhas cujo tipo é `record_id` (filtro "Filtra Linha Tipo")."""
    return [line for line, line_type in zip(lines, line_types) if line_type == record_id]


def lines_containing(lines: Sequence[str], needle: str) -> list[str]:
    """Linhas que contêm `needle` sem diferenciar maiúsculas (filtro "Valor em Busca")."""
    wanted = needle.lower()
    return [line for line in lines if wanted and wanted in line.lower()]


def _matches_in_line(lowered: str, wanted: str, line_number: int, first_column: int) -> Iterator[TextPosition]:
    offset = lowered.find(wanted, max(first_column, 1) - 1)
    while offset >= 0:
        yield TextPosition(line_number, offset + 1)
        offset = lowered.find(wanted, offset + 1)


def _overlaps(previous: TextPosition, current: TextPosition, length: int) -> bool:
    return previous.line == current.line and current.column < previous.column + length

"""Operações em lote sobre linhas: sequenciar, substituir e ajustar quantidade.

Todas as funções são puras: recebem a lista de linhas e devolvem uma nova.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

from layouttxt.domain.field_context import overwrite_at


def format_sequence_number(number: int, size: int) -> str:
    """Número com zeros à esquerda, mantendo os `size` dígitos da direita.

    Exemplo:
        >>> format_sequence_number(12345, 3)
        '345'
    """
    return str(number).zfill(size)[-size:] if size > 0 else ""


@dataclass(frozen=True)
class SequenceOptions:
    """Parâmetros da tela "Sequenciar" (colunas 1-based)."""

    start: int
    increment: int
    end: int
    size: int
    column: int
    at_line_end: bool
    only_line_type: bool


def apply_sequence(
    lines: Sequence[str], line_types: Sequence[str], record_id: str, first_line: int, options: SequenceOptions
) -> list[str]:
    """Numera as linhas a partir de `first_line` (1-based) até `options.end`.

    Exemplo:
        >>> opts = SequenceOptions(1, 1, 99, 2, 2, False, False)
        >>> apply_sequence(["A", "B"], ["", ""], "", 1, opts)
        ['A01', 'B02']
    """
    result = list(lines)
    number = options.start
    for index in range(max(first_line, 1) - 1, len(result)):
        if options.only_line_type and line_types[index] != record_id:
            continue
        result[index] = _write_sequence(result[index], number, options)
        number += options.increment
        if number > options.end:
            break
    return result


def _write_sequence(line: str, number: int, options: SequenceOptions) -> str:
    text = format_sequence_number(number, options.size)
    if not options.at_line_end:
        return overwrite_at(line, options.column, text)
    padded = line.ljust(options.size)
    return padded[: len(padded) - options.size] + text


class Direction(Enum):
    """Direção do "Substitui" a partir da linha atual."""

    DOWN = "Para baixo"
    ALL = "Todas"
    UP = "Para cima"


@dataclass(frozen=True)
class SubstitutionRequest:
    """Parâmetros da tela "Substitui".

    `new_text` recebe o tamanho e devolve o texto (fixo ou gerado).
    `max_count` None significa "Todas".
    """

    current_line: int
    column: int
    size: int
    new_text: Callable[[int], str]
    direction: Direction
    record_id: str
    any_line_type: bool
    only_same_value: bool
    max_count: int | None


def substitute_values(
    lines: Sequence[str], line_types: Sequence[str], request: SubstitutionRequest
) -> tuple[list[str], int]:
    """Substitui o trecho (coluna, tamanho) nas linhas selecionadas (ex.: `substitute_values(["ab"], [""], req)`)."""
    result = list(lines)
    reference = _slice(result[request.current_line - 1], request)
    count = 0
    for index in _line_indexes(len(result), request):
        if not _should_substitute(result[index], line_types[index], reference, request):
            continue
        result[index] = overwrite_at(result[index], request.column, request.new_text(request.size))
        count += 1
        if request.max_count is not None and count >= request.max_count:
            break
    return result, count


def _line_indexes(total: int, request: SubstitutionRequest) -> range:
    current = request.current_line - 1
    if request.direction is Direction.UP:
        return range(current, -1, -1)
    return range(0 if request.direction is Direction.ALL else current, total)


def _should_substitute(line: str, line_type: str, reference: str, request: SubstitutionRequest) -> bool:
    if not request.any_line_type and line_type != request.record_id:
        return False
    return not request.only_same_value or _slice(line, request) == reference


def _slice(line: str, request: SubstitutionRequest) -> str:
    return line[request.column - 1 : request.column - 1 + request.size]


def resize_line_type(
    lines: Sequence[str], line_types: Sequence[str], record_id: str, template: str, target: int
) -> list[str]:
    """Exclui as últimas linhas do tipo ou cria cópias de `template` após a última.

    Exemplo:
        >>> resize_line_type(["H", "D1", "T"], ["H", "D", "T"], "D", "D1", 3)
        ['H', 'D1', 'D1', 'D1', 'T']
    """
    positions = [index for index, line_type in enumerate(line_types) if line_type == record_id]
    if target < 0:
        raise ValueError(f"Quantidade {target} inválida; esperado inteiro >= 0")
    if target <= len(positions):
        removed = set(positions[target:])
        return [line for index, line in enumerate(lines) if index not in removed]
    insert_at = positions[-1] + 1 if positions else len(lines)
    return list(lines[:insert_at]) + [template] * (target - len(positions)) + list(lines[insert_at:])

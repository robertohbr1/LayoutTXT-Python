"""Modelo de layout de arquivo texto posicional.

Equivale aos recordsets `rst` (todos os campos) e `rstTipo` (campos com
Tag = "X", que identificam o tipo de linha) do projeto VB original.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

KEY_TAG = "X"


@dataclass(frozen=True)
class FieldSpec:
    """Um campo de um tipo de registro (uma linha do CSV de layout).

    Colunas são 1-based, como no layout e na barra de status.

    Exemplo:
        >>> FieldSpec("0", "Tipo", 1, 1, 1, "F", "0", "", "X").extract("0ABC")
        '0'
    """

    record_id: str
    name: str
    start: int
    end: int
    size: int
    field_type: str
    fixed: str
    description: str
    tag: str

    @property
    def is_key(self) -> bool:
        """True se o campo identifica o tipo de linha (Tag = "X")."""
        return self.tag.strip().upper() == KEY_TAG

    def extract(self, line: str) -> str:
        """Retorna o conteúdo do campo na linha (equivale a `Mid`)."""
        return line[self.start - 1 : self.start - 1 + self.size]

    def contains_column(self, column: int) -> bool:
        """True se a coluna (1-based) pertence ao campo."""
        return self.start <= column <= self.end

    def matches_key(self, line: str) -> bool:
        """True se o valor da linha é igual a `fixed` ou a uma das opções `a|b|c`."""
        value = self.extract(line).strip()
        return value == self.fixed or value in self.fixed.split("|")


@dataclass(frozen=True)
class Layout:
    """Coleção ordenada de campos lida de um CSV de layout.

    Exemplo:
        >>> layout.identify("0123...")  # doctest: +SKIP
        '0'
    """

    fields: tuple[FieldSpec, ...]

    def record_ids(self) -> list[str]:
        """Ids de tipo de linha na ordem em que aparecem (os do combo "Filtra")."""
        ids: list[str] = []
        for record_id, _ in self._key_groups():
            if not ids or ids[-1] != record_id:
                ids.append(record_id)
        return ids

    def fields_of(self, record_id: str) -> list[FieldSpec]:
        """Todos os campos de um tipo de linha, na ordem do layout."""
        return [field for field in self.fields if field.record_id == record_id]

    def field_at(self, record_id: str, column: int) -> FieldSpec | None:
        """Primeiro campo do tipo `record_id` que contém a coluna (1-based)."""
        for field in self.fields_of(record_id):
            if field.contains_column(column):
                return field
        return None

    def field_named(self, record_id: str, name: str) -> FieldSpec | None:
        """Campo do tipo `record_id` com o nome informado."""
        for field in self.fields_of(record_id):
            if field.name == name:
                return field
        return None

    def identify(self, line: str) -> str:
        """Id do tipo da linha ou "" se nenhum grupo de campos-chave casar.

        Mesma regra de `RetTipo` do VB: o primeiro grupo contíguo de campos
        chave em que todos os campos casam define o tipo.
        """
        for record_id, keys in self._key_groups():
            if all(key.matches_key(line) for key in keys):
                return record_id
        return ""

    def identify_all(self, lines: list[str]) -> list[str]:
        """Tipo de cada linha (equivale a `CarregaTipoLinha`)."""
        return [self.identify(line) for line in lines]

    def _key_groups(self) -> list[tuple[str, list[FieldSpec]]]:
        keys = [field for field in self.fields if field.is_key]
        return [(rid, list(group)) for rid, group in groupby(keys, lambda f: f.record_id)]

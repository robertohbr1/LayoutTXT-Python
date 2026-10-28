"""Geração de valores aleatórios para preencher campos (combo "Gerar Novo")."""

from __future__ import annotations

import random
import string
from enum import Enum
from typing import Callable, Sequence

from layouttxt.domain.brazil_ids import CNPJ_LENGTH, CPF_LENGTH, cnpj_check_digits, cpf_check_digits

_Builder = Callable[[int], str]
_ALNUM = string.digits + string.ascii_uppercase
_HEAD_OFFICE_BRANCH = "0001"


class GeneratorKind(Enum):
    """Tipos de valor gerado; o texto é o exibido nos combos."""

    CPF = "CPF"
    CNPJ_HEAD_OFFICE = "CNPJ Matriz"
    CNPJ_ANY = "CNPJ Qualquer"
    DIGITS = "Só Número"
    ALNUM = "Letra & Números"
    NAME = "Nome"


MIN_SIZE: dict[GeneratorKind, int] = {
    GeneratorKind.CPF: CPF_LENGTH,
    GeneratorKind.CNPJ_HEAD_OFFICE: CNPJ_LENGTH,
    GeneratorKind.CNPJ_ANY: CNPJ_LENGTH,
}


class ValueGenerator:
    """Gera CPF, CNPJ, números, alfanuméricos e nomes com tamanho fixo.

    `rng` e `names` são injetados para permitir testes determinísticos.

    Exemplo:
        >>> ValueGenerator(random.Random(1), ["ANA"]).generate(GeneratorKind.NAME, 5)
        'ANA A'
    """

    def __init__(self, rng: random.Random, names: Sequence[str]) -> None:
        self._rng = rng
        self._names = [name for name in names if name]

    def generate(self, kind: GeneratorKind, size: int) -> str:
        """Valor com exatamente `size` caracteres (CPF/CNPJ com zeros à esquerda)."""
        minimum = MIN_SIZE.get(kind, 1)
        if size < minimum:
            raise ValueError(f"Tamanho {size} inválido para {kind.value}; esperado >= {minimum}")
        return self._builders()[kind](size)

    def cpf(self) -> str:
        """CPF válido com 11 dígitos."""
        base = self.digits(9)
        return base + cpf_check_digits(base)

    def cnpj(self, head_office: bool) -> str:
        """CNPJ válido; `head_office` força a filial 0001 (matriz)."""
        base = self.digits(8) + _HEAD_OFFICE_BRANCH if head_office else self.digits(12)
        return base + cnpj_check_digits(base)

    def digits(self, size: int) -> str:
        """Sequência de `size` dígitos."""
        return "".join(self._rng.choice(string.digits) for _ in range(size))

    def alnum(self, size: int) -> str:
        """Sequência de `size` letras maiúsculas e dígitos."""
        return "".join(self._rng.choice(_ALNUM) for _ in range(size))

    def name(self, size: int) -> str:
        """Nomes aleatórios separados por espaço, cortados em `size`."""
        if not self._names:
            return self._letters_with_spaces(size)
        text = ""
        while len(text) < size:
            text += self._rng.choice(self._names) + " "
        return text[:size]

    def _letters_with_spaces(self, size: int) -> str:
        # Mesmo fallback do VB (RetNumeroAlfa Index 2): espaço a cada 5 posições.
        chars = [" " if pos % 5 == 0 else self._rng.choice(string.ascii_uppercase) for pos in range(1, size + 1)]
        return "".join(chars)

    def _builders(self) -> dict[GeneratorKind, _Builder]:
        return {
            GeneratorKind.CPF: lambda size: self.cpf().rjust(size, "0"),
            GeneratorKind.CNPJ_HEAD_OFFICE: lambda size: self.cnpj(True).rjust(size, "0"),
            GeneratorKind.CNPJ_ANY: lambda size: self.cnpj(False).rjust(size, "0"),
            GeneratorKind.DIGITS: self.digits,
            GeneratorKind.ALNUM: self.alnum,
            GeneratorKind.NAME: self.name,
        }

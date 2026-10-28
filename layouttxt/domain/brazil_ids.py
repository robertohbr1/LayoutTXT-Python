"""Cálculo e validação de dígitos verificadores de CPF e CNPJ."""

from __future__ import annotations

CPF_LENGTH = 11
CNPJ_LENGTH = 14
_CPF_WEIGHTS_1 = tuple(range(10, 1, -1))
_CPF_WEIGHTS_2 = tuple(range(11, 1, -1))
_CNPJ_WEIGHTS_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_CNPJ_WEIGHTS_2 = (6,) + _CNPJ_WEIGHTS_1


def cpf_check_digits(base9: str) -> str:
    """Dois dígitos verificadores para os 9 primeiros dígitos de um CPF.

    Exemplo:
        >>> cpf_check_digits("111444777")
        '35'
    """
    _require_digits(base9, 9, "CPF base")
    first = _mod11_digit(base9, _CPF_WEIGHTS_1)
    return first + _mod11_digit(base9 + first, _CPF_WEIGHTS_2)


def cnpj_check_digits(base12: str) -> str:
    """Dois dígitos verificadores para os 12 primeiros dígitos de um CNPJ.

    Exemplo:
        >>> cnpj_check_digits("112223330001")
        '81'
    """
    _require_digits(base12, 12, "CNPJ base")
    first = _mod11_digit(base12, _CNPJ_WEIGHTS_1)
    return first + _mod11_digit(base12 + first, _CNPJ_WEIGHTS_2)


def is_valid_cpf(value: str) -> bool:
    """Valida CPF aceitando pontuação (`.`, `-`, `/`), como `ValidaCPF`.

    Exemplo:
        >>> is_valid_cpf("111.444.777-35")
        True
    """
    digits = strip_punctuation(value)
    if len(digits) != CPF_LENGTH or not digits.isdigit() or _weighted_sum(digits[:9], _CPF_WEIGHTS_1) == 0:
        return False
    return cpf_check_digits(digits[:9]) == digits[9:]


def is_valid_cnpj(value: str) -> bool:
    """Valida CNPJ aceitando pontuação, como `ValidaCNPJ`.

    Exemplo:
        >>> is_valid_cnpj("11.222.333/0001-81")
        True
    """
    digits = strip_punctuation(value)
    if len(digits) != CNPJ_LENGTH or not digits.isdigit() or _weighted_sum(digits[:12], _CNPJ_WEIGHTS_1) == 0:
        return False
    return cnpj_check_digits(digits[:12]) == digits[12:]


def strip_punctuation(value: str) -> str:
    """Remove espaços nas pontas e os caracteres `.`, `-` e `/`."""
    return value.strip().replace(".", "").replace("-", "").replace("/", "")


def format_cpf(digits: str) -> str:
    """Formata 11 dígitos como `000.000.000-00`."""
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def format_cnpj(digits: str) -> str:
    """Formata 14 dígitos como `00.000.000/0000-00`."""
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def _mod11_digit(digits: str, weights: tuple[int, ...]) -> str:
    remainder_digit = 11 - (_weighted_sum(digits, weights) % 11)
    return "0" if remainder_digit > 9 else str(remainder_digit)


def _weighted_sum(digits: str, weights: tuple[int, ...]) -> int:
    return sum(int(digit) * weight for digit, weight in zip(digits, weights))


def _require_digits(value: str, length: int, label: str) -> None:
    if len(value) != length or not value.isdigit():
        raise ValueError(f"{label}={value!r} inválido; esperado {length} dígitos")

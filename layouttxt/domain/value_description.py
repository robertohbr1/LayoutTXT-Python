"""Interpretação legível do valor de um campo conforme o tipo (coluna TP).

Equivale ao preenchimento de `txtValor2` em `txtValor_Change` do VB.
Tipos suportados: `IN(a@desc|b)`, `ECPF/CNPJ`, `ECEP`, `N`, `N0`, `Nn` e
datas `D<padrão>` (ex.: `DAAAAMMDD`, `DDDMMAA`).
"""

from __future__ import annotations

import datetime
import re

from layouttxt.domain.brazil_ids import format_cnpj, format_cpf

UNKNOWN_OPTION = "** Desconhecido **"
INVALID_DATE = "Data Inválida"
_LEADING_DIGITS = re.compile(r"\d*")


def describe_value(field_type: str, value: str) -> str:
    """Texto explicativo do valor; "" quando o tipo não tem interpretação.

    Exemplo:
        >>> describe_value("N2", "000012345")
        '123,45'
    """
    kind, rest = field_type[:1].upper(), field_type[1:]
    describers = {"I": _describe_option, "E": _describe_special, "N": _describe_number, "D": _describe_date}
    describer = describers.get(kind)
    return describer(field_type, rest, value) if describer else ""


def parse_options(field_type: str) -> list[tuple[str, str]]:
    """Opções de um tipo `IN(...)` como pares (código, descrição).

    Exemplo:
        >>> parse_options("IN(F@Física|J)")
        [('F', 'Física'), ('J', '')]
    """
    body = field_type[3:-1] if field_type.endswith(")") else field_type[3:]
    return [_split_option(option) for option in body.split("|")]


def format_ptbr_number(number: float, decimals: int) -> str:
    """Número com separador de milhar `.` e decimal `,`.

    Exemplo:
        >>> format_ptbr_number(1234.5, 2)
        '1.234,50'
    """
    text = f"{number:,.{decimals}f}"
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def vb_val(text: str) -> int:
    """Inteiro dos dígitos iniciais, ignorando espaços (como `Val("0" & x)`)."""
    digits = _LEADING_DIGITS.match(text.replace(" ", ""))
    return int(digits.group()) if digits and digits.group() else 0


def _split_option(option: str) -> tuple[str, str]:
    code, _, description = option.partition("@")
    return code, description


def _describe_option(field_type: str, _rest: str, value: str) -> str:
    for code, description in parse_options(field_type):
        if code == value:
            return description
    return UNKNOWN_OPTION


def _describe_special(_field_type: str, rest: str, value: str) -> str:
    digits = value.strip()
    if not digits.isdigit():
        return ""
    if rest.upper() == "CPF/CNPJ":
        return _describe_document(digits)
    if rest.upper() in ("CEP", "CEP_B"):
        return _describe_zip(digits)
    return ""


def _describe_document(digits: str) -> str:
    if len(digits) <= 11 or set(digits[:-11]) == {"0"}:
        return format_cpf(digits.zfill(11)[-11:])
    return format_cnpj(digits.zfill(14)[-14:])


def _describe_zip(digits: str) -> str:
    if int(digits) == 0:
        return ""
    padded = digits.zfill(8)[-8:]
    return f"{padded[:5]}-{padded[5:]}"


def _describe_number(_field_type: str, rest: str, value: str) -> str:
    if rest == "":
        return value
    if not rest.isdigit():
        return ""
    decimals = int(rest)
    return format_ptbr_number(vb_val(value) / (10**decimals), decimals)


def _describe_date(_field_type: str, pattern: str, value: str) -> str:
    pattern = pattern.upper()
    if len(value.strip()) < len(pattern):
        return ""
    parsed = _parse_date(pattern, value)
    if parsed is None or _format_date(pattern, parsed) != value[: len(pattern)]:
        return INVALID_DATE
    return parsed.strftime("%d/%m/%Y")


def _parse_date(pattern: str, value: str) -> datetime.date | None:
    year_size = 4 if "AAAA" in pattern else 2
    try:
        year = int(_slice(pattern, value, "A" * year_size))
        month = int(_slice(pattern, value, "MM"))
        day = int(_slice(pattern, value, "DD"))
        return datetime.date(_expand_year(year, year_size), month, day)
    except ValueError:
        return None


def _slice(pattern: str, value: str, token: str) -> str:
    position = pattern.find(token)
    if position < 0:
        raise ValueError(f"Padrão de data {pattern!r} sem {token!r}; esperado DD, MM e AA/AAAA")
    return value[position : position + len(token)]


def _expand_year(year: int, year_size: int) -> int:
    # Mesma janela do DateSerial do VB: 00-29 => 2000, 30-99 => 1900.
    if year_size == 4:
        return year
    return 2000 + year if year < 30 else 1900 + year


def _format_date(pattern: str, date: datetime.date) -> str:
    year_token = "AAAA" if "AAAA" in pattern else "AA"
    year_text = f"{date.year:04d}" if year_token == "AAAA" else f"{date.year % 100:02d}"
    return pattern.replace(year_token, year_text).replace("MM", f"{date.month:02d}").replace("DD", f"{date.day:02d}")

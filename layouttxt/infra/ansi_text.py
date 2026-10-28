"""Leitura e gravação de arquivos texto ANSI (Windows-1252), como o FSO do VB."""

from __future__ import annotations

import codecs
import shutil
from dataclasses import dataclass
from pathlib import Path

ENCODING = "cp1252"
UTF8 = "utf-8"
_PASSTHROUGH = "layouttxt_passthrough"
BACKUP_SUFFIX = ".Bak"


def _passthrough(error: UnicodeError) -> tuple[str | bytes, int]:
    # Bytes sem mapeamento no cp1252 (0x81, 0x8D...) viram U+0081... e voltam
    # intactos na gravação, para não corromper arquivos ao salvar.
    if isinstance(error, UnicodeDecodeError):
        chunk = error.object[error.start : error.end]
        return "".join(chr(byte) for byte in chunk), error.end
    if isinstance(error, UnicodeEncodeError):
        chunk = error.object[error.start : error.end]
        return bytes(ord(char) if ord(char) < 256 else ord("?") for char in chunk), error.end
    raise error


codecs.register_error(_PASSTHROUGH, _passthrough)


@dataclass(frozen=True)
class LoadedText:
    """Conteúdo com quebras normalizadas para `\\n`, a quebra e a codificação originais."""

    content: str
    newline: str
    encoding: str = ENCODING


def decode_ansi(raw: bytes) -> LoadedText:
    """Decodifica bytes (UTF-8 se válido, senão ANSI) e normaliza quebras de linha.

    UTF-8 é aceito para que layouts versionados no GitHub (texto UTF-8)
    continuem abrindo com acentos corretos.

    Exemplo:
        >>> decode_ansi(b"a\\r\\nb").content
        'a\\nb'
    """
    encoding = UTF8 if _is_utf8(raw) else ENCODING
    text = raw.decode(encoding, errors=_PASSTHROUGH)
    newline = "\r\n" if "\r\n" in text else ("\r" if "\r" in text and "\n" not in text else "\n")
    return LoadedText(text.replace("\r\n", "\n").replace("\r", "\n"), newline, encoding)


def encode_ansi(content: str, newline: str, encoding: str = ENCODING) -> bytes:
    """Codifica texto com quebras `\\n` usando a quebra e a codificação informadas.

    Exemplo:
        >>> encode_ansi("a\\nb", "\\r\\n")
        b'a\\r\\nb'
    """
    return content.replace("\n", newline).encode(encoding, errors=_PASSTHROUGH)


def _is_utf8(raw: bytes) -> bool:
    # Só considera UTF-8 se houver bytes não-ASCII; ASCII puro segue como ANSI.
    if raw.isascii():
        return False
    try:
        raw.decode(UTF8)
    except UnicodeDecodeError:
        return False
    return True


class AnsiFileStore:
    """Acesso a arquivos em disco; injetado na UI para poder ser substituído em testes."""

    def read(self, path: str) -> LoadedText:
        """Lê o arquivo; lança `OSError` se não existir ou estiver bloqueado."""
        return decode_ansi(Path(path).read_bytes())

    def write(self, path: str, content: str, newline: str, backup: bool, encoding: str = ENCODING) -> None:
        """Grava o arquivo; com `backup`, copia antes o original para `<arquivo>.Bak`."""
        target = Path(path)
        if backup and target.exists():
            shutil.copyfile(target, target.with_name(target.name + BACKUP_SUFFIX))
        target.write_bytes(encode_ansi(content, newline, encoding))

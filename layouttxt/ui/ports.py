"""Interfaces de interação com o usuário, injetadas nos painéis.

Permitem trocar as caixas de diálogo do Tk por fakes nos testes.
"""

from __future__ import annotations

from typing import Protocol


class Dialogs(Protocol):
    """Caixas de mensagem e perguntas (MsgBox / InputBox / CommonDialog)."""

    def info(self, message: str) -> None:
        """Mensagem informativa."""

    def ask_yes_no(self, message: str, default_yes: bool = True) -> bool:
        """Pergunta Sim/Não."""

    def ask_yes_no_cancel(self, message: str) -> bool | None:
        """Pergunta Sim/Não/Cancelar; None = Cancelar."""

    def ask_string(self, message: str, initial: str = "") -> str | None:
        """Pede um texto; None se cancelado."""

    def ask_open_path(self, initial: str, extension: str = "") -> str | None:
        """Seleciona um arquivo existente; None se cancelado."""

    def ask_save_path(self, initial: str) -> str | None:
        """Seleciona onde gravar um arquivo; None se cancelado."""


class Clipboard(Protocol):
    """Área de transferência."""

    def get_text(self) -> str:
        """Texto atual ("" se vazio ou não-texto)."""

    def set_text(self, text: str) -> None:
        """Substitui o conteúdo."""

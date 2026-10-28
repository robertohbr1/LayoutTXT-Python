"""Implementações Tk de `Dialogs` e `Clipboard`."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

APP_TITLE = "LayoutTXT"


class TkDialogs:
    """Caixas de diálogo nativas do Tk, com a janela principal como dona."""

    def __init__(self, owner: tk.Misc) -> None:
        self._owner = owner

    def info(self, message: str) -> None:
        messagebox.showinfo(APP_TITLE, message, parent=self._owner)

    def ask_yes_no(self, message: str, default_yes: bool = True) -> bool:
        default = messagebox.YES if default_yes else messagebox.NO
        return messagebox.askyesno(APP_TITLE, message, default=default, parent=self._owner)

    def ask_yes_no_cancel(self, message: str) -> bool | None:
        return messagebox.askyesnocancel(APP_TITLE, message, parent=self._owner)

    def ask_string(self, message: str, initial: str = "") -> str | None:
        return simpledialog.askstring(APP_TITLE, message, initialvalue=initial, parent=self._owner)

    def ask_open_path(self, initial: str, extension: str = "") -> str | None:
        types = [(f"*.{extension}", f"*.{extension}"), ("Todos", "*.*")] if extension else [("Todos", "*.*")]
        chosen = filedialog.askopenfilename(
            parent=self._owner, initialdir=_initial_dir(initial), initialfile=os.path.basename(initial), filetypes=types
        )
        return chosen or None

    def ask_save_path(self, initial: str) -> str | None:
        chosen = filedialog.asksaveasfilename(
            parent=self._owner, initialdir=_initial_dir(initial), initialfile=os.path.basename(initial)
        )
        return chosen or None


class TkClipboard:
    """Área de transferência via widget Tk."""

    def __init__(self, owner: tk.Misc) -> None:
        self._owner = owner

    def get_text(self) -> str:
        try:
            return self._owner.clipboard_get()
        except tk.TclError:
            return ""

    def set_text(self, text: str) -> None:
        self._owner.clipboard_clear()
        self._owner.clipboard_append(text)


def _initial_dir(path: str) -> str:
    folder = os.path.dirname(path)
    return folder if folder and os.path.isdir(folder) else os.getcwd()

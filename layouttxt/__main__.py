"""Ponto de entrada da aplicação LayoutTXT."""

from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path

from layouttxt.domain.value_generator import ValueGenerator
from layouttxt.infra.ansi_text import AnsiFileStore
from layouttxt.infra.names_source import load_names
from layouttxt.infra.settings_store import JsonSettingsStore, default_settings_path
from layouttxt.ui.main_window import MainWindow
from layouttxt.ui.tk_dialogs import TkClipboard, TkDialogs

ICON_PATH = Path(__file__).resolve().parent / "resources" / "LayoutTXT.ico"


def main() -> None:
    """Inicia a janela principal do LayoutTXT (ex.: `python -m layouttxt`)."""
    root = tk.Tk()
    if ICON_PATH.exists():
        root.iconbitmap(default=str(ICON_PATH))
    files = AnsiFileStore()
    settings = JsonSettingsStore(default_settings_path())
    generator = ValueGenerator(random.Random(), load_names(files))
    MainWindow(root, files, settings, generator, TkDialogs(root), TkClipboard(root))
    root.mainloop()


if __name__ == "__main__":
    main()
